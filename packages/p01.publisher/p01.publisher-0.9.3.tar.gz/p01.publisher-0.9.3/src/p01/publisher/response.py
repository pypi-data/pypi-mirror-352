##############################################################################
#
# Copyright (c) 2013 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Publication

$Id: response.py 5279 2025-05-16 11:48:45Z roger.ineichen $
"""
from __future__ import absolute_import

import six
from future import standard_library

standard_library.install_aliases()
from builtins import map
from builtins import str
from builtins import object
from six import ensure_text

import re
import sys
import logging
from io import BytesIO
from io import StringIO

if sys.version_info[0] > 2:
    import http.cookies as cookies
    from urllib.parse import quote
    from html import escape
    str = str
    six.string_types = (str, bytes)
else:
    import http.cookies as cookies
    from urllib.parse import quote
    from cgi import escape

import zope.interface
import zope.component
import zope.contenttype.parse
import zope.publisher.interfaces
from zope.publisher.interfaces.http import IResult
from zope.publisher.http import status_codes
from zope.publisher.http import status_reasons
from zope.publisher.http import extract_host
from zope.publisher.http import getCharsetUsingRequest
from zope.publisher.browser import isHTML
from zope.publisher.http import DirectResult
from zope.security.proxy import isinstance
from zope.exceptions.exceptionformatter import print_exception
from zope.exceptions.exceptionformatter import format_exception


import p01.json.api
import p01.jsonrpc.interfaces
from p01.publisher import interfaces
from p01.publisher._compat import PYTHON2
from p01.publisher._compat import CLASS_TYPES
from p01.publisher._compat import _u


logger = logging.getLogger()

DEBUG = logging.DEBUG

# Default Encoding
ENCODING = 'UTF-8'

eventlog = logging.getLogger('eventlog')

start_of_header_search=re.compile(b'(<head[^>]*>)', re.I).search
base_re_search=re.compile(b'(<base.*?>)',re.I).search
isRelative = re.compile("[-_.!~*a-zA-z0-9'()@&=+$,]+(/|$)").match

# not just text/* but RFC 3023 and */*+xml

unicode_mimetypes_re = re.compile(
    r"^text\/.*$|^.*\/xml.*$|^.*\+xml$|^application/json$")

def is_text_html(content_type):
    return content_type.startswith('text/html')


@zope.interface.implementer(interfaces.IResponse)
class BaseResponse(object):
    """Base Response Class
    """

    __slots__ = (
        '_result',    # The result of the application call
        '_request',   # The associated request (if any)
        )


    def __init__(self):
        self._request = None

    def setResult(self, result):
        """See IPublisherResponse"""
        self._result = result

    def handleException(self, exc_info):
        """See IPublisherResponse"""
        # We want exception to be formatted to native strings. Pick
        # respective io class depending on python version.
        f = BytesIO() if PYTHON2 else StringIO()
        print_exception(exc_info[0], exc_info[1], exc_info[2], 100, f)
        self.setResult(f.getvalue())

    def internalError(self):
        """See IPublisherResponse"""
        pass

    def reset(self):
        """See IPublisherResponse"""
        pass

    def retry(self):
        """See IPublisherResponse"""
        raise NotImplementedError("p01.publisher does not support retry")


@zope.interface.implementer(interfaces.IHTTPResponse)
class HTTPResponse(BaseResponse):

    __slots__ = (
        '_headers',
        '_cookies',
        '_status',              # The response status (usually an integer)
        '_reason',              # The reason that goes with the status
        '_status_set',          # Boolean: status explicitly set
        '_charset',             # String: character set for the output
        )


    def __init__(self):
        super(HTTPResponse, self).__init__()
        self.reset()


    def reset(self):
        """See IResponse"""
        super(HTTPResponse, self).reset()
        self._headers = {}
        self._cookies = {}
        self._status = 599
        self._reason = 'No status set'
        self._status_set = False
        self._charset = None

    def setStatus(self, status, reason=None):
        """See IHTTPResponse"""
        if status is None:
            status = 200
        try:
            status = int(status)
        except ValueError:
            if isinstance(status, six.string_types):
                status = status.lower()
            # Use a standard status code, falling back to 500 for
            # nonstandard values (such as "valueerror")
            status = status_codes.get(status, 500)
        self._status = status

        if reason is None:
            reason = status_reasons.get(status, "Unknown")

        self._reason = reason
        self._status_set = True

    def getStatus(self):
        """See IHTTPResponse"""
        return self._status

    def getStatusString(self):
        """See IHTTPResponse"""
        return '%i %s' % (self._status, self._reason)

    def setHeader(self, name, value, literal=False):
        """See IHTTPResponse"""
        name = ensure_text(name)
        value = ensure_text(value)
        if not literal:
            name = name.lower()
        self._headers[name] = [value]

    def addHeader(self, name, value):
        """See IHTTPResponse"""
        values = self._headers.setdefault(name, [])
        values.append(value)

    def getHeader(self, name, default=None, literal=False):
        """See IHTTPResponse"""
        key = name.lower()
        name = literal and name or key
        result = self._headers.get(name)
        if result:
            return result[0]
        return default

    def getHeaders(self):
        """See IHTTPResponse

        - Status is not a header
        - X-Powered-By is always the 1st header
        - then come user-provided headers, sorted alphabetically (this is the
        part that I changed -- previously user-supplied headers came in
        dictionary order)
        - then come Set-Cookie headers, with cookie names sorted alphabetically
        (by the Cookie stdlib module)

        """
        result = []
        headers = self._headers

        # the order is not alphabetical, but it's deterministic
        # see: https://github.com/zopefoundation/zope.publisher/issues/8
        result.append(
            ("X-Powered-By", "Zope (www.zope.org), Python (www.python.org)"))

        for key, values in sorted(list(headers.items()), key=lambda x: x[0].lower()):
            if key.lower() == key:
                # only change non-literal header names
                key = '-'.join([k.capitalize() for k in key.split('-')])
            result.extend([(key, val) for val in values])

        result.extend([tuple(cookie.split(': ', 1))
                       for cookie in self._cookie_list()])

        return result

    def appendToCookie(self, name, value):
        """See IHTTPResponse"""
        cookies = self._cookies
        if name in cookies:
            cookie = cookies[name]
        else:
            cookie = cookies[name] = {}
        if 'value' in cookie:
            cookie['value'] = '%s:%s' % (cookie['value'], value)
        else:
            cookie['value'] = value

    def expireCookie(self, name, **kw):
        """See IHTTPResponse"""
        dict = {'max_age':0, 'expires':'Wed, 31-Dec-97 23:59:59 GMT'}
        for k, v in list(kw.items()):
            if v is not None:
                dict[k] = v
        cookies = self._cookies
        if name in cookies:
            # Cancel previous setCookie().
            del cookies[name]
        self.setCookie(name, 'deleted', **dict)

    def setCookie(self, name, value, **kw):
        """See IHTTPResponse"""
        cookies = self._cookies
        cookie = cookies.setdefault(name, {})
        for k, v in list(kw.items()):
            if v is not None:
                cookie[k.lower()] = v
        cookie['value'] = value

    def getCookie(self, name, default=None):
        """See IHTTPResponse"""
        return self._cookies.get(name, default)

    def setResult(self, result):
        """See IHTTPResponse"""
        if IResult.providedBy(result):
            r = result
        else:
            r = zope.component.queryMultiAdapter((result, self._request), IResult)
            if r is None:
                if isinstance(result, six.string_types):
                    r = result
                elif result is None:
                    r = ''
                else:
                    raise TypeError(
                        'The result should be None, a string, or adaptable to IResult.')
        if isinstance(r, six.string_types):
            r, headers = self._implicitResult(r)

            # normalize all header names and values to unicode
            self._headers.update(
                dict((ensure_text(k), [ensure_text(v)]) for (k, v) in headers)
            )

            r = (r,)  # chunking should be much larger than per character

        self._result = r
        if not self._status_set:
            self.setStatus(200)

    def consumeBody(self):
        """See IHTTPResponse"""
        return b''.join(self._result)


    def consumeBodyIter(self):
        """See IHTTPResponse"""
        return self._result

    def _implicitResult(self, body):
        encoding = getCharsetUsingRequest(self._request) or 'utf-8'
        content_type = self.getHeader('content-type')

        if isinstance(body, str):
            ct = content_type
            if not unicode_mimetypes_re.match(ct):
                raise ValueError(
                    'Unicode results must have a text, RFC 3023, RFC 4627,'
                    ' or +xml content type.')

            major, minor, params = zope.contenttype.parse.parse(ct)

            if 'charset' in params:
                encoding = params['charset']

            try:
                body = body.encode(encoding)
            except (UnicodeEncodeError, LookupError):
                encoding = 'utf-8'
                body = body.encode(encoding)

            if (major, minor) != ('application', 'json'):
                params['charset'] = encoding
            content_type = "%s/%s" % (major, minor)
            if params:
                content_type += ";" + ";".join(k + "=" + v for k, v in list(params.items()))

        if content_type:
            headers = [
                (ensure_text(u'content-type'), ensure_text(content_type)),
                (ensure_text(u'content-length'), ensure_text(str(len(body))))
            ]
        else:
            headers = [
                (ensure_text(u'content-length'), ensure_text(str(len(body))))
            ]

        return body, headers

    def handleException(self, exc_info):
        """Calls self.setBody() with an error response."""
        t, v = exc_info[:2]
        if isinstance(t, CLASS_TYPES):
            if issubclass(t, zope.publisher.interfaces.Redirect):
                self.redirect(v.getLocation(), trusted=v.getTrusted())
                return
            title = tname = t.__name__
        else:
            title = tname = _u(t)

        # Throwing non-protocol-specific exceptions is a good way
        # for apps to control the status code.
        self.setStatus(tname)

        body = self._html(title, "A server error occurred." )
        self.setHeader("Content-Type", "text/html")
        self.setResult(body)

    def internalError(self):
        """See IPublisherResponse"""
        self.setStatus(500, u"The engines can't take any more, Jim!")

    def _html(self, title, content):
        t = escape(title)
        return (
            u"<html><head><title>%s</title></head>\n"
            u"<body><h2>%s</h2>\n"
            u"%s\n"
            u"</body></html>\n" %
            (t, t, content)
            )

    def redirect(self, location, status=None, trusted=False):
        """Causes a redirection without raising an error"""

        # convert to a string, as the location could be non-string
        # convertable to string, for example, an URLGetter instance
        location = str(location)

        __traceback_info__ = location

        if not trusted:
            target_host = extract_host(location)
            if target_host:
                app_host = extract_host(self._request.getApplicationURL())
                if target_host != app_host:
                    raise ValueError(
                        "Untrusted redirect to host %r not allowed."
                        % target_host)

        if status is None:
            # parse the HTTP version and set default accordingly
            if (self._request.get("SERVER_PROTOCOL","HTTP/1.0") <
                "HTTP/1.1"):
                status=302
            else:
                status=303

        self.setStatus(status)
        self.setHeader('Location', location)
        self.setResult(DirectResult(()))
        return location

    def _cookie_list(self):
        try:
            c = cookies.SimpleCookie()
        except cookies.CookieError as e:
            eventlog.warn(e)
            return []
        for name, attrs in list(self._cookies.items()):
            # In python-2.x, Cookie module expects plain bytes (not unicode).
            # However, in python-3.x, latin-1 unicode string is expected (not
            # bytes).  We make this distinction clear here.
            if not isinstance(name, str):
                name = name.encode('utf-8')

            cookieval = attrs['value'].encode(ENCODING)
            if PYTHON2:
                c[name] = cookieval
            else:
                c[name] = cookieval.decode('latin-1')

            for k,v in list(attrs.items()):
                if k == 'value':
                    continue
                if k == 'secure':
                    if v:
                        c[name]['secure'] = True
                    continue
                if k == 'max_age':
                    k = 'max-age'
                elif k == 'comment':
                    # Encode rather than throw an exception
                    v = quote(v.encode('utf-8'), safe="/?:@&+")
                c[name][k] = str(v)
        return str(c).splitlines()

    def write(*_):
        raise TypeError(
            "The HTTP response write method is no longer supported. "
            "See the file httpresults.txt in the zope.publisher package "
            "for more information."
            )

    def retry(self):
        """Returns a response object to be used in a retry attempt"""
        raise NotImplementedError("p01.publisher does not support retry")


@zope.interface.implementer(interfaces.IBrowserResponse)
class BrowserResponse(HTTPResponse):
    """Browser response
    """

    __slots__ = (
        '_base', # The base href
        )

    def _implicitResult(self, body):
        content_type = self.getHeader('content-type')
        if content_type is None and self._status != 304:
            if isHTML(body):
                content_type = u'text/html'
            else:
                content_type = u'text/plain'
            self.setHeader(u'x-content-type-warning', u'guessed from content')
            self.setHeader(u'content-type', content_type)

        body, headers = super(BrowserResponse, self)._implicitResult(body)
        body = self.__insertBase(body)
        # Update the Content-Length header to account for the inserted
        # <base> tag.
        headers = [
            (name, value) for name, value in headers
            if name != u'content-length'
            ]
        headers.append((u'content-length', ensure_text(str(len(body)))))
        return body, headers

    def __insertBase(self, body):
        # Only insert a base tag if content appears to be html.
        content_type = self.getHeader('content-type', '')
        if content_type and not is_text_html(content_type):
            return body

        if self.getBase():
            if body:
                match = start_of_header_search(body)
                if match is not None:
                    index = match.start(0) + len(match.group(0))
                    ibase = base_re_search(body)
                    if ibase is None:
                        # Make sure the base URL is not a unicode string.
                        base = self.getBase()
                        if not isinstance(base, bytes):
                            encoding = getCharsetUsingRequest(self._request) or 'utf-8'
                            base = self.getBase().encode(encoding)
                        #body = (b'%s\n<base href="%s" />\n%s' %
                        #        (body[:index], base, body[index:]))
                        body = b''.join([body[:index],
                                         b'\n<base href="',
                                         base,
                                         b'" />\n',
                                         body[index:]])
        return body

    def getBase(self):
        return getattr(self, '_base', '')

    def setBase(self, base):
        self._base = base

    def redirect(self, location, status=None, trusted=False):
        base = getattr(self, '_base', '')
        if base and isRelative(str(location)):
            l = base.rfind('/')
            if l >= 0:
                base = base[:l+1]
            else:
                base += '/'
            location = base + location

        # TODO: HTTP redirects must provide an absolute location, see
        #       http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.30
        #       So, what if location is relative and base is unknown?  Uncomment
        #       the following and you'll see that it actually happens.
        #
        # if isRelative(str(location)):
        #     raise AssertionError('Cannot determine absolute location')

        return super(BrowserResponse, self).redirect(location, status, trusted)

    def reset(self):
        super(BrowserResponse, self).reset()
        self._base = ''


class JSONRPCResponse(HTTPResponse):
    """JSON-RPC Response"""

    def premarshal(self, result):
        """Get json data out of security proxy without to remove the proxy"""
        if isinstance(result, dict):
            return dict([(self.premarshal(k), self.premarshal(v))
                         for (k, v) in list(result.items())])
        elif isinstance(result, (tuple, list)):
            return list(map(self.premarshal, result))
        else:
            return result

    def getJSONString(self, data):
        """Convert json data to string

        This hook can get used for enhanced json data convertion using custom
        json encoder, decoder pattern
        """
        return p01.json.api.jsonWriter(data)

    def setResult(self, result):
        """The incoming result is a jsonrpc error view given from publication
        handleError method or a json data dict.

        The outgoing result is a dict with the following format.

        The version 1.0 and 1.1 provides a response dict with the following
        arguments:

        id -- json request id
        result -- result or null on error
        error -- error or null if result is Ok

        The version 2.0 provides a response dict with the following named
        paramters:

        jsonrpc -- jsonrpc version 2.0 or higher in future versions
        id -- json request id
        result -- result if no error is raised
        error -- error if any given

        """
        jsonId = self._request.jsonId
        jsonVersion = self._request.jsonVersion

        if p01.jsonrpc.interfaces.IJSONRPCErrorView.providedBy(result):
            if self._request.jsonVersion == "1.0":
                wrapper = {'result': None,
                           'error': result.message,
                           'id': self._request.jsonId}
            elif self._request.jsonVersion == "1.1":
                wrapper = {'version': self._request.jsonVersion,
                           'error': result.message,
                           'id': self._request.jsonId}
            else:
                wrapper = {'jsonrpc': self._request.jsonVersion,
                           'error': {'code': result.code,
                                     'message': result.message,
                                     'data': result.data},
                           'id': self._request.jsonId}

            try:
                result = self.getJSONString(wrapper)
                body = self._prepareResult(result)
                super(JSONRPCResponse, self).setResult(DirectResult((body,)))
                logger.log(DEBUG, "Exception: %s" % result)
                # error response is not really an error, it's valid response
                self.setStatus(200)
            except:
                # Catch all exceptions at this point
                self.handleException(sys.exc_info())
                return

        else:
            result = self.premarshal(result)
            if jsonVersion == "1.0":
                wrapper = {'result': result, 'error': None, 'id': jsonId}
            elif jsonVersion == "1.1":
                wrapper = {
                    'version': jsonVersion, 'result': result, 'id': jsonId}
            else:
                wrapper = {
                    'jsonrpc': jsonVersion, 'result': result, 'id': jsonId}
            result = self.getJSONString(wrapper)
            body = self._prepareResult(result)
            super(JSONRPCResponse, self).setResult(DirectResult((body,)))
            logger.log(DEBUG, "%s" % result)

    def _prepareResult(self, result):
        """Return result as unicode with correct content type and encoding"""
        encoding = getCharsetUsingRequest(self._request) or 'utf-8'
        enc = encoding.lower()
        if not enc in p01.jsonrpc.interfaces.JSON_CHARSETS:
            encoding = 'utf-8'
        # convert to unicode (ujson doesn't if no unicode input is given)
        if not isinstance(result, str):
            try:
                result = str(result, 'utf-8')
            except (UnicodeDecodeError, UnicodeTranslateError):
                result = str(result, 'utf-8', 'replace')
        body = result.encode(encoding)
        charset = encoding
        # set content type
        self.setHeader('content-type', "application/json;charset=%s"
                       % charset)
        return body

    def handleException(self, exc_info):
        # only legacy Exception where we didn't define a view for get handled
        # by this method. All exceptions where we have a view registered for
        # get handled by the setResult method based on the given
        # IJSONRPCErrorView
        logger.log(logging.ERROR, "".join(format_exception(
            exc_info[0], exc_info[1], exc_info[2], with_filenames=True)))

        t, value = exc_info[:2]
        s = '%s: %s' % (getattr(t, '__name__', t), value)
        if self._request.jsonVersion == "1.0":
            wrapper = {'result': None,
                       'error': s,
                       'id': self._request.jsonId}
        elif self._request.jsonVersion == "1.1":
            wrapper = {'version': self._request.jsonVersion,
                       'error': s,
                       'id': self._request.jsonId}
        else:
            # this only happens if error handling was running into en error or
            # if we didn't define an IJSONRPCErrorView for a given error
            wrapper = {'jsonrpc': self._request.jsonVersion,
                       'error': {'code': -32603,
                                 'message': 'Internal error',
                                 'data': s},
                       'id': self._request.jsonId}

        result = self.getJSONString(wrapper)
        body = self._prepareResult(result)
        super(JSONRPCResponse, self).setResult(DirectResult((body,)))
        logger.log(DEBUG, "Exception: %s" % result)
        self.setStatus(200)
