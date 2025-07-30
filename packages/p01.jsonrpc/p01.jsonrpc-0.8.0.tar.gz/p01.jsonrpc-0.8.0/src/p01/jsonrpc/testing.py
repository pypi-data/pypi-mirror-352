##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import base64
import copy
import re
import rfc822
import sys
import json
import doctest
import persistent
from cStringIO import StringIO

PY3 = sys.version_info[0] == 3
if PY3: # pragma: no coverr
    from urllib import parse as urlparse
    from http.cookies import SimpleCookie
    def unquote(string):
        if not string:
            return b''
        res = string.split(b'%')
        if len(res) != 1:
            string = res[0]
            for item in res[1:]:
                try:
                    string += bytes([int(item[:2], 16)]) + item[2:]
                except ValueError:
                    string += b'%' + item
        return string
    def url_unquote(s):
        return unquote(s.encode('ascii')).decode('latin-1')
else:
    import urlparse
    from Cookie import SimpleCookie
    from urllib import unquote as url_unquote

import transaction

import zope.interface
import zope.component
import zope.testing.cleanup
import zope.container.interfaces
from zope.component import hooks

import p01.publisher.interfaces
import p01.publisher.application
import p01.publisher.testing

import p01.json.exceptions
import p01.json.proxy
import p01.json.transport

from p01.jsonrpc import layer
from p01.jsonrpc.publication import JSONRPCPublication
from p01.jsonrpc.publisher import JSONRPCRequest
from p01.jsonrpc.publisher import MethodPublisher
from p01.jsonrpc.publisher import JSON_RPC_VERSION

SCHEME_RE = re.compile(r'^[a-z]+:', re.I)


###############################################################################
#
# test application
#
###############################################################################

class IJSONRPCTestApplication(zope.container.interfaces.IContainer,
        p01.publisher.interfaces.IApplication):
    """Test application offering container"""

    def get(key, default=None):
        """Returns item or defualt"""

    def __getitem__(key):
        """Returns item or defualt"""


class JSONRPCTestApplication(p01.publisher.application.Application):
    """Test application"""

    zope.interface.implements(IJSONRPCTestApplication)

    def __init__(self):
        super(JSONRPCTestApplication, self).__init__()
        self._data = {}

    def __setitem__(self, key, obj):
        self._data[key] = obj
        obj.__parent__ = self
        obj.__name__ = key

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        try:
            return self._data[key]
        except KeyError as e:
            return default

    def __delitem__(self, key):
        del self._data[key]

    def __repr__(self):
        return '<%s>' % (self.__class__.__name__)


def setUpTestApplication():
    """Setup test application used as root and for test traversing"""
    app = JSONRPCTestApplication()
    zope.component.provideUtility(app, p01.publisher.interfaces.IApplication,
        '')
    return app


def getRootFolder():
    return zope.component.getUtility(p01.publisher.interfaces.IApplication)


headerre = re.compile(r'(\S+): (.+)$')
def split_header(header):
    return headerre.match(header).group(1, 2)


basicre = re.compile('Basic (.+)?:(.+)?$')
def auth_header(header):
    match = basicre.match(header)
    if match:
        u, p = match.group(1, 2)
        if u is None:
            u = ''
        if p is None:
            p = ''
        auth = base64.encodestring('%s:%s' % (u, p))
        return 'Basic %s' % auth[:-1]
    return header


###############################################################################
#
# JSONRPC Test proxy
#
###############################################################################

class ResponseWrapper(object):
    """A wrapper that adds several introspective methods to a response."""

    def __init__(self, response, path, omit=()):
        self._response = response
        self._path = path
        self.omit = omit
        self._body = None

    def getOutput(self):
        """Returns the full HTTP output (headers + body)"""
        body = self.getBody()
        omit = self.omit
        headers = [x
                   for x in self._response.getHeaders()
                   if x[0].lower() not in omit]
        headers.sort()
        headers = '\n'.join([("%s: %s" % (n, v)) for (n, v) in headers])
        statusline = '%s %s' % (self._response._request['SERVER_PROTOCOL'],
                                self._response.getStatusString())
        if body:
            return '%s\n%s\n\n%s' %(statusline, headers, body)
        else:
            return '%s\n%s\n' % (statusline, headers)

    def getBody(self):
        """Returns the response body"""
        if self._body is None:
            self._body = ''.join(self._response.consumeBody())

        return self._body

    def getPath(self):
        """Returns the path of the request"""
        return self._path

    def __getattr__(self, attr):
        return getattr(self._response, attr)

    __str__ = getOutput


class JSONRPCTestTransport(p01.json.transport.Transport):
    """Test transport using wsgi application and it's publisher.

    It can be used like a normal transport, including support for basic
    authentication.
    """

    cookies = None
    verbose = False
    jsonReader = None
    contentType = None
    handleErrors = True

    def __init__(self, app, contentType="application/json-rpc", jsonReader=None,
        verbose=0, username=None, password=None, bearer=None):
        super(JSONRPCTestTransport, self).__init__(contentType=contentType,
            jsonReader=jsonReader, verbose=verbose)
        self.app = app
        # optional crednetials
        self.username = username
        self.password = password
        self.bearer = bearer
        # store cookies between consecutive requests
        self.cookies = SimpleCookie()

    # cookies
    def httpCookie(self, path):
         """Return self.cookies as an HTTP_COOKIE environment value."""
         l = [m.OutputString().split(';')[0] for m in self.cookies.values()
              if path.startswith(m['path'])]
         return '; '.join(l)

    def loadCookies(self, envstring):
        self.cookies.load(envstring)

    def saveCookies(self, response):
        """Save cookies from the response."""
        for k,v in response._cookies.items():
            k = k.encode('utf8')
            self.cookies[k] = v['value'].encode('utf8')
            if v.has_key('path'):
                self.cookies[k]['path'] = v['path']

    def getEnviron(self, method, path, protocol):
        """Get environment based on first input line

        The first request line looks  somethng like:

        POST / HTTP/1.0\n

        """
        if SCHEME_RE.search(path):
            scheme, netloc, path, qs, fragment = urlparse.urlsplit(path)
            if fragment:
                raise TypeError(
                    "Path cannot contain a fragment (%r)" % fragment)
            if qs:
                path += '?' + qs
            if ':' not in netloc:
                if scheme == 'http':
                    netloc += ':80'
                elif scheme == 'https':
                    netloc += ':443'
                else:
                    raise TypeError("Unknown scheme: %r" % scheme)
        else:
            scheme = 'http'
            netloc = 'localhost:90'
        if path and '?' in path:
            path_info, query_string = path.split('?', 1)
            path_info = url_unquote(path_info)
        else:
            path_info = url_unquote(path)
            query_string = ''
        return {
            'HTTP_COOKIE': self.httpCookie(path),
            'HTTP_HOST': netloc,
            'HTTP_REFERER': netloc,
            'REQUEST_METHOD': method,
            'SCRIPT_NAME': '',
            'PATH_INFO': path_info or '',
            'QUERY_STRING': query_string,
            'SERVER_NAME': netloc.split(':')[0],
            'SERVER_PORT': netloc.split(':')[1],
            'SERVER_PROTOCOL': protocol,
        }

    # request handling
    def request(self, host, handler, request_body, verbose=0):
        """Handle request"""
        if not handler:
            handler = '/'
        request = "POST %s HTTP/1.0\n" % (handler,)
        request += "Content-Length: %i\n" % len(request_body)
        request += "Content-Type: application/json-rpc\n"

        host, extra_headers, x509 = self.get_host_info(host)
        if extra_headers:
            request += "Authorization: %s\n" % (
                dict(extra_headers)["Authorization"])
        elif self.username is not None and self.password is not None:
            credentials = "%s:%s" % (self.username, self.password)
            request += "Authorization: Basic %s\n" % base64.encodestring(
                credentials).replace("\012", "")
        elif self.bearer is not None:
            request += "Authorization: Bearer %s\n" % self.bearer

        request += "\n" + request_body
        response = self.doRequest(request, handleErrors=self.handleErrors)
        errcode = response.getStatus()
        errmsg = response.getStatusString()
        # This is not the same way that the normal transport deals with the
        # headers.
        headers = response.getHeaders()

        if errcode != 200:
            raise p01.json.exceptions.ProtocolError(host + handler, errcode,
                errmsg, headers)

        return self._parse_response(StringIO(response.getBody()), sock=None)

    def doPublish(self, instream, environment):
        """Publish input stream and return request"""
        request = self.app.publisher(instream, environment)
        return self.app.publisher.publish(request,
            handleErrors=self.handleErrors)

    def doRequest(self, request_string, handleErrors=True):
        """Process request and return response"""
        # commit work done by previous request
        transaction.commit()

        # discard leading white space to make call layout simpler
        request_string = request_string.lstrip()

        # split off and parse the command line
        l = request_string.find('\n')
        command_line = request_string[:l].rstrip()
        method, path, protocol = command_line.split()
        environment = self.getEnviron(method, path, protocol)

        request_string = request_string[l+1:]
        instream = StringIO(request_string)

        headers = [split_header(header)
                   for header in rfc822.Message(instream).headers]
        for name, value in headers:
            name = ('_'.join(name.upper().split('-')))
            if name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                name = 'HTTP_' + name
            environment[name] = value.rstrip()

        auth_key = 'HTTP_AUTHORIZATION'
        if environment.has_key(auth_key):
            environment[auth_key] = auth_header(environment[auth_key])

        old_site = hooks.getSite()
        hooks.setSite(None)

        request = self.doPublish(instream, environment)

        response = ResponseWrapper(
            request.response, path,
            omit=('x-content-type-warning', 'x-powered-by'),
            )

        self.saveCookies(response)
        hooks.setSite(old_site)

        return response


def getJSONRPCTestProxy(uri, app=None, transport=None, encoding=None,
    verbose=None, jsonId=None, handleErrors=True, jsonVersion=JSON_RPC_VERSION,
    contentType="application/json-rpc", jsonReader=None, jsonWriter=None,
    username=None, password=None, bearer=None, cookies=None):
    """Test JSONRPCProxy using wsgi app and it's publisher for processing"""
    if transport is not None and username is not None and password is not None:
        raise Exception(
            "getJSONRPCTestProxy can't use transport and username and password. "
            "Use only transport or username and password. Setup authentication "
            "in your own transport class if needed.")
    if app is None:
        app = zope.component.getUtility(p01.publisher.interfaces.IApplication)
    publisher = p01.publisher.publisher.Publisher
    wsgi_app = p01.publisher.application.WSGIApplication(app, publisher,
        handleErrors)
    if transport is None:
        transport = JSONRPCTestTransport(wsgi_app, contentType=contentType,
            jsonReader=jsonReader, verbose=verbose, username=username,
            password=password, bearer=bearer)
    if isinstance(transport, JSONRPCTestTransport):
        transport.handleErrors = handleErrors
    if cookies is not None:
        transport.cookies = cookies
    return p01.json.proxy.JSONRPCProxy(uri, transport=transport,
        encoding=encoding, jsonId=jsonId, jsonVersion=jsonVersion,
        contentType=contentType, jsonWriter=jsonWriter, verbose=verbose)


def getCookies(proxy):
    """Get response cookies from proxy"""
    return proxy._JSONRPCProxy__transport.cookies

def setCookies(proxy, cookies):
    """Set request cookies given from previous proxy to new proxy"""
    proxy._JSONRPCProxy__transport.cookies = cookies


###############################################################################
#
# Test layer
#
###############################################################################

p01.publisher.testing.defineLayer("JSONRPCTestingLayer", "ftesting.zcml",
    allow_teardown=True)


###############################################################################
#
# Test component
#
###############################################################################

class IJSONRPCTestLayer(layer.IJSONRPCLayer):
    """JSON-RPC test layer interface used for zcml testing."""


class IJSONRPCTestSkin(IJSONRPCTestLayer):
    """The IJSONRPCTestSkin testing skin based on IJSONRPCLayer."""


class IA(zope.interface.Interface):
    """First content stub interface."""


class A(persistent.Persistent):
    """First content stub."""

    zope.interface.implements(IA)


class IB(zope.interface.Interface):
    """First content stub interface."""


class B(persistent.Persistent):
    """First content stub."""

    zope.interface.implements(IB)


class MethodsA(MethodPublisher):
    """Method publisher test class."""

    def hello(self):
        return "Hello A World"


class MethodsB(MethodPublisher):
    """Method publisher test class."""

    def hello(self):
        return "Hello B World"


class TestRequest(JSONRPCRequest):
    """modeled after zope.publisher.xmlrpc.TestRequest"""
    def __init__(self, body_instream=None, environ=None,
                 response=None, **kw):

        _testEnv =  {
            'SERVER_URL':         'http://127.0.0.1',
            'HTTP_HOST':          '127.0.0.1',
            'CONTENT_LENGTH':     '0',
            'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
            }

        if environ:
            _testEnv.update(environ)
        if kw:
            _testEnv.update(kw)
        if body_instream is None:
            body_instream = StringIO('')

        super(TestRequest, self).__init__(
            body_instream, _testEnv, response)


class CookieHandler(object):

    def __init__(self, *args, **kw):
        # Somewhere to store cookies between consecutive requests
        self.cookies = SimpleCookie()
        super(CookieHandler, self).__init__(*args, **kw)

    def httpCookie(self, path):
        """Return self.cookies as an HTTP_COOKIE environment value."""
        l = [m.OutputString().split(';')[0] for m in self.cookies.values()
             if path.startswith(m['path'])]
        return '; '.join(l)

    def loadCookies(self, envstring):
        self.cookies.load(envstring)

    def saveCookies(self, response):
        """Save cookies from the response."""
        # Urgh - need to play with the response's privates to extract
        # cookies that have been set
        # TODO: extend the IHTTPRequest interface to allow access to all
        # cookies
        # TODO: handle cookie expirations
        for k, v in response._cookies.items():
            k = k.encode('utf8') if bytes is str else k
            val = v['value']
            val = val.encode('utf8') if bytes is str else val
            self.cookies[k] = val
            if 'path' in v:
                self.cookies[k]['path'] = v['path']


# class HTTPCaller(functional.HTTPCaller):
#     """HTTPCaller for JSON."""

#     def chooseRequestClass(self, method, path, environment):
#         """Choose and return a request class and a publication class"""
#         request_cls, publication_cls = \
#             super(HTTPCaller, self).chooseRequestClass(method, path,
#                 environment)

#         content_type = environment.get('CONTENT_TYPE', '')
#         is_json = content_type.startswith('application/json')

#         if method in ('GET', 'POST', 'HEAD'):
#             if (method == 'POST' and is_json):
#                 request_cls = JSONRPCRequest
#                 publication_cls = JSONRPCPublication

#         return request_cls, publication_cls


# class HTTPCaller(CookieHandler):
#     """HTTPCaller for JSON."""

#     def chooseRequestClass(self, method, path, environment):
#         """Choose and return a request class and a publication class"""
#         request_cls, publication_cls = \
#             super(HTTPCaller, self).chooseRequestClass(method, path,
#                 environment)

#         content_type = environment.get('CONTENT_TYPE', '')
#         is_json = content_type.startswith('application/json')

#         if method in ('GET', 'POST', 'HEAD'):
#             if (method == 'POST' and is_json):
#                 request_cls = JSONRPCRequest
#                 publication_cls = JSONRPCPublication

#         return request_cls, publication_cls

#     def __call__(self, request_string, handle_errors=True, form=None):
#         # Commit work done by previous python code.
#         commit()

#         # Discard leading white space to make call layout simpler
#         request_string = request_string.lstrip()

#         # split off and parse the command line
#         l = request_string.find('\n')
#         command_line = request_string[:l].rstrip()
#         request_string = request_string[l + 1:]
#         method, path, protocol = command_line.split()

#         # If we don't feed bytes to Python 3, it gets stuck in a loop
#         # and ultimately raises HTTPException: got more than 100 headers.
#         instream = io.BytesIO(request_string.encode("latin-1")
#                               if not isinstance(request_string, bytes)
#                               else request_string)
#         environment = {
#             "HTTP_COOKIE": self.httpCookie(path),
#             "HTTP_HOST": 'localhost',
#             "REQUEST_METHOD": method,
#             "SERVER_PROTOCOL": protocol,
#             "REMOTE_ADDR": '127.0.0.1',
#         }

#         headers = [split_header(header)
#                    for header in headers_factory(instream).headers]
#         for name, value in headers:
#             name = ('_'.join(name.upper().split('-')))
#             if name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
#                 name = 'HTTP_' + name
#             environment[name] = value.rstrip()

#         auth_key = 'HTTP_AUTHORIZATION'
#         if auth_key in environment:
#             environment[auth_key] = auth_header(environment[auth_key])

#         old_site = hooks.getSite()
#         hooks.setSite(None)

#         request_cls, publication_cls = self.chooseRequestClass(method, path,
#                                                                environment)
#         app = FunctionalTestSetup().getApplication()

#         request = app._request(
#             path, instream,
#             environment=environment,
#             request=request_cls, publication=publication_cls)
#         if ISkinnable.providedBy(request):
#             # only ISkinnable requests have skins
#             setDefaultSkin(request)

#         if form is not None:
#             if request.form:
#                 raise ValueError("only one set of form values can be provided")
#             request.form = form

#         # request = publish(request, handle_errors=handle_errors)
#         request = self.app.publisher.publish(request,
#             handle_errors=handle_errors)

#         response = ResponseWrapper(
#             request.response, path, request,
#             omit=('x-content-type-warning', 'x-powered-by'),
#             )

#         self.saveCookies(response)
#         hooks.setSite(old_site)

#         # sync Python connection:
#         getRootFolder()._p_jar.sync()

#         return response


###############################################################################
#
# Doctest setup
#
###############################################################################

def FunctionalDocFileSuite(*paths, **kw):
    # use our custom HTTPCaller and layer
    globs = kw.setdefault('globs', {})
    globs['getRootFolder'] = getRootFolder
    kw['package'] = doctest._normalize_module(kw.get('package'))
    # _prepare_doctest_keywords(kw)
    p01.publisher.testing.prepareDocTestKeywords(kw)
    suite = doctest.DocFileSuite(*paths, **kw)
    suite.layer = JSONRPCTestingLayer
    return suite


###############################################################################
#
# Test helper, make us independent from zope.app.testing
#
###############################################################################

# Setup of test text files as modules
import sys

# Evil hack to make pickling work with classes defined in doc tests
class NoCopyDict(dict):
    def copy(self):
        return self

class FakeModule:
    """A fake module."""

    def __init__(self, dict):
        self.__dict = dict

    def __getattr__(self, name):
        try:
            return self.__dict[name]
        except KeyError:
            raise AttributeError(name)


def setUpTestAsModule(test, name=None):
    if name is None:
        if test.globs.haskey('__name__'):
            name = test.globs['__name__']
        else:
            name = test.globs.name

    test.globs['__name__'] = name
    test.globs = NoCopyDict(test.globs)
    sys.modules[name] = FakeModule(test.globs)


def tearDownTestAsModule(test):
    del sys.modules[test.globs['__name__']]
    test.globs.clear()


###############################################################################
#
# Unittest setup
#
###############################################################################

def setUp(test):
    setUpTestAsModule(test, name='README')


def tearDown(test):
    # ensure that we cleanup everything
    zope.testing.cleanup.cleanUp()
    tearDownTestAsModule(test)
