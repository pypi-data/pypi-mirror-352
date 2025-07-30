# -*- coding: utf-8 -*-
"""
    pip_services4_http.controller.HttpEndpoint
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Http endpoint implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json
import re
import time
from threading import Thread
from typing import List, Optional, Callable

import bottle
from beaker.middleware import SessionMiddleware
from bottle import request, response
from pip_services4_commons.errors import ConfigException, ConnectionException
from pip_services4_components.config import IConfigurable, ConfigParams

from pip_services4_components.context import IContext
from pip_services4_components.refer import IReferenceable, IReferences
from pip_services4_components.run import IOpenable
from pip_services4_data.validate import Schema
from pip_services4_observability.count import CompositeCounters
from pip_services4_observability.log import CompositeLogger

from . import IRegisterable
from .HttpResponseSender import HttpResponseSender
from .SSLCherryPyServer import SSLCherryPyServer
from ..connect.HttpConnectionResolver import HttpConnectionResolver


class HttpEndpoint(IOpenable, IConfigurable, IReferenceable):
    """
    Used for creating HTTP endpoints. An endpoint is a URL, at which a given service can be accessed by a client.

    ### Configuration parameters ###
        Parameters to pass to the :func:`configure` method for component configuration:

        - cors_headers - a comma-separated list of allowed CORS headers
        - cors_origins - a comma-separated list of allowed CORS origins

        - connection(s) - the connection resolver's connections;
            - "connection.discovery_key" - the key to use for connection resolving in a discovery service;
            - "connection.protocol" - the connection's protocol;
            - "connection.host" - the target host;
            - "connection.port" - the target port;
            - "connection.uri" - the target URI.

        - credential - the HTTPS credentials:
            - "credential.ssl_key_file" - the SSL private key in PEM
            - "credential.ssl_crt_file" - the SSL certificate in PEM
            - "credential.ssl_ca_file" - the certificate authorities (root cerfiticates) in PEM


    ### References ###
        A logger, counters, and a connection resolver can be referenced by passing the following references to the object's :func:`set_references` method:
            - `*:logger:*:*:1.0`           (optional) :class:`ILogger <pip_services4_observability.log.ILogger.ILogger>` components to pass log messages
            - `*:counters:*:*:1.0`         (optional) :class:`ICounters <pip_services4_observability.count.ICounters.ICounters>` components to pass collected measurements
            - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services4_config.connect.IDiscovery.IDiscovery>` controller to resolve connection

    Example:

    .. code-block:: python

        def my_method(_config, _references):
            endpoint = HttpEndpoint()
            if (_config)
                endpoint.configure(_config)
            if (_references)
                endpoint.setReferences(_references)
            # ...

            endpoint.open(context)
            # ...
    """
    _default_config = ConfigParams.from_tuples("connection.protocol", "http",
                                               "connection.host", "0.0.0.0",
                                               "connection.port", 3000,
                                               "credential.ssl_key_file", None,
                                               "credential.ssl_crt_file", None,
                                               "credential.ssl_ca_file", None,
                                               "options.maintenance_enabled", False,
                                               "options.request_max_size", 1024 * 1024,
                                               "options.file_max_size", 200 * 1024 * 1024,
                                               "connection.connect_timeout", 60000,
                                               "connection.debug", True)

    _debug = False

    def __init__(self):
        """
        Creates HttpEndpoint
        """
        self.__service = None
        self.__server = None
        self.__maintenance_enabled: bool = False
        self.__file_max_size = 200 * 1024 * 1024
        self.__protocol_upgrade_enabled: bool = False
        self.__uri: str = None

        self.__connection_resolver: HttpConnectionResolver = HttpConnectionResolver()
        self.__logger: CompositeLogger = CompositeLogger()
        self.__counters: CompositeCounters = CompositeCounters()
        self.__registrations: List[IRegisterable] = []
        self.__allowed_headers: List[str] = ["trace_id"]
        self.__allowed_origins: List[str] = []

    def configure(self, config: ConfigParams):
        """
        Configures this HttpEndpoint using the given configuration parameters.
        - connection(s) - the connection resolver's connections;
            - "connection.discovery_key" - the key to use for connection resolving in a discovery service;
            - "connection.protocol" - the connection's protocol;
            - "connection.host" - the target host;
            - "connection.port" - the target port;
            - "connection.uri" - the target URI.

        :param config: configuration parameters, containing a "connection(s)" section.
        """
        config = config.set_defaults(self._default_config)
        self.__connection_resolver.configure(config)

        bottle.BaseRequest.MEMFILE_MAX = config.get_as_long('options.request_max_size')
        self.__file_max_size = config.get_as_long_with_default('options.file_max_size', self.__file_max_size)
        self.__maintenance_enabled = config.get_as_boolean_with_default('options.maintenance_enabled',
                                                                        self.__maintenance_enabled)
        self.__protocol_upgrade_enabled = config.get_as_boolean_with_default('options.protocol_upgrade_enabled',
                                                                             self.__protocol_upgrade_enabled)
        self._debug = config.get_as_boolean_with_default('options.debug', self._debug)

        headers = config.get_as_string_with_default("cors_headers", "").split(",")
        for header in headers:
            if header != '':
                self.__allowed_headers = list(filter(lambda h: h != header, self.__allowed_headers))
                self.__allowed_headers.append(header)

        origins = config.get_as_string_with_default("cors_origins", "").split(',')
        for origin in origins:
            origin = origin.strip()
            if origin != '':
                self.__allowed_origins = list(filter(lambda h: h != origin, self.__allowed_origins))
                self.__allowed_origins.append(origin)

    def set_references(self, references: IReferences):
        """
        Sets references to this endpoint's logger, counters, and connection resolver.

        - *:logger:*:*:1.0           (optional) :class:`ILogger <pip_services4_observability.log.ILogger.ILogger>` components to pass log messages
        - *:counters:*:*:1.0         (optional) :class:`ICounters <pip_services4_observability.count.ICounters.ICounters>` components to pass collected measurements
        - *:discovery:*:*:1.0        (optional) :class:`IDiscovery <pip_services4_config.connect.IDiscovery.IDiscovery>` controller to resolve connection

        :param references: an IReferences object, containing references to a logger, counters, and a connection resolver.
        """
        self.__logger.set_references(references)
        self.__counters.set_references(references)
        self.__connection_resolver.set_references(references)

    def is_open(self) -> bool:
        """
        Checks if the component is opened.

        :return: whether or not this endpoint is open with an actively listening REST server.
        """
        return not (self.__server is None)

    def open(self, context: Optional[IContext]):
        """
        Opens a connection using the parameters resolved by the referenced connection resolver and creates a REST server (service) using the set options and parameters.

        :param context: (optional) transaction id to trace execution through call chain.
        """
        if self.is_open():
            return

        connection = self.__connection_resolver.resolve(context)
        if connection is None:
            raise ConfigException(context, "NO_CONNECTION", "Connection for REST client is not defined")
        self.__uri = connection.get_as_string('uri')

        # verify https with bottle

        certfile = None
        keyfile = None

        if connection.get_as_string_with_default('protocol', 'http') == 'https':
            certfile = connection.get_as_nullable_string('ssl_crt_file')
            keyfile = connection.get_as_nullable_string('ssl_key_file')

        # Create instance of bottle application
        self.__service = SessionMiddleware(bottle.Bottle(catchall=True, autojson=True)).app

        self.__service.config['catchall'] = True
        self.__service.config['autojson'] = True

        # Enable CORS requests
        self.__service.add_hook('after_request', self.__enable_cors)

        self.__service.add_hook('after_request', self.__do_maintance)
        self.__service.add_hook('after_request', self.__no_cache)
        self.__service.add_hook('before_request', self.__add_compatibility)

        # Register routes
        # self.__perform_registrations()

        def start_server():
            self.__service.run(server=self.__server, debug=self._debug)

        # self.__perform_registrations()

        host = connection.get_as_string('host')
        port = connection.get_as_integer('port')
        # Starting service
        try:
            self.__server = SSLCherryPyServer(host=host, port=port, certfile=certfile, keyfile=keyfile)

            # Start server in thread
            Thread(target=start_server, daemon=True).start()
            # Time for start server
            time.sleep(0.01)

            # Give 2 sec for initialization
            self.__connection_resolver.register(context)
            self.__logger.debug(context, f"Opened REST service at {self.__uri}", )
            self.__perform_registrations()

            # Route registration for OPTIONS (for preflight requests)
            self.__register_options_route()

        except Exception as ex:
            self.__server = None

            raise ConnectionException(context, 'CANNOT_CONNECT', 'Opening REST service failed') \
                .wrap(ex).with_details('url', self.__uri)

    def close(self, context: Optional[IContext]):
        """
        Closes this endpoint and the REST server (service) that was opened earlier.

        :param context: (optional) transaction id to trace execution through call chain.
        """
        try:
            if not (self.__server is None):
                self.__server.shutdown()
                self.__service.close()
                self.__logger.debug(
                    context, f"Closed REST service at {self.__uri}")

            self.__server = None
            self.__service = None
            self.__uri = None
        except Exception as ex:
            self.__logger.warn(context, "Failed while closing REST service: " + str(ex))

    def register(self, registration: IRegisterable):
        """
        Registers a registerable object for dynamic endpoint discovery.

        :param registration: the registration to add.
        """
        self.__registrations.append(registration)

    def unregister(self, registration: IRegisterable):
        """
        Unregisters a registerable object, so that it is no longer used in dynamic endpoint discovery.

        :param registration: the registration to remove.
        """
        self.__registrations.remove(registration)

    def __perform_registrations(self):
        for registration in self.__registrations:
            registration.register()

    def __fix_route(self, route: str) -> str:
        if route is not None and len(route) > 0:
            if route[0] != '/':
                route = f'/{route}'
            return route

        return ''
    
    def __register_options_route(self):
        """
        Route registration for OPTIONS (for preflight requests).
        Responds to any route with method OPTIONS to support CORS.
        """
        def handle_options(path=None):
            self.__enable_cors()
            self.__do_maintance()
            self.__no_cache()
            self.__add_compatibility()
            return ''

        # Register wildcard route for OPTIONS method
        self.__service.route('/<path:re:.*>', method='OPTIONS', callback=handle_options)


    def register_route(self, method: str, route: str, schema: Schema, handler: Callable):
        """
        Registers an action in this objects REST server (service) by the given method and route.

        :param method: the HTTP method of the route.

        :param route: the route to register in this object's REST server (service).

        :param schema: the schema to use for parameter validation.

        :param handler: the action to perform at the given route.
        """
        method = method.upper()
        # if method == 'DELETE':
        #     method = 'DEL'

        route = self.__fix_route(route)

        def wrapper(*args, **kwargs):
            try:
                if isinstance(schema, Schema):
                    params = self.__get_data() or {}
                    params.update(kwargs)
                    trace_id = None if not params else params.get('trace_id')
                    schema.validate_and_throw_exception(trace_id, params, False)

                return handler(*args, **kwargs)
            except Exception as ex:
                # hack the redirect response in bottle
                if isinstance(ex, bottle.HTTPResponse):
                    handler(*args, **kwargs)
                return HttpResponseSender.send_error(ex)

        self.__service.route(route, method, wrapper)

    def __get_data(self) -> Optional[dict]:
        result = {}
        if request.json or request.query:
            for k, v in request.query.dict.items():
                result[k] = ''.join(v)
            if request.json is not None and request.json != 'null':
                json_body = request.json if not isinstance(request.json, str) else json.loads(
                    request.json)
                result.update({'body': json_body})
            return result
        else:
            return None

    def __enable_cors(self):
        response.headers['Access-Control-Max-Age'] = '5'
        response.headers['Access-Control-Allow-Origin'] = ', '.join(self.__allowed_origins)
        response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
        response.headers[
            'Access-Control-Allow-Headers'] = ', '.join(self.__allowed_headers)

    def __do_maintance(self):
        """
        :return: maintenance error code
        """
        # Make this more sophisticated
        if self.__maintenance_enabled:
            response.headers['Retry-After'] = 3600
            response.status = 503

    def __no_cache(self):
        """
        Prevents IE from caching REST requests
        """
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = 0

    def __add_compatibility(self):

        def inner(name):
            if request.query:
                param = request.query[name]
                if param:
                    return param
            if request.body:
                param = request.json[name]
                if param:
                    return param
            if request.params:
                param = request.params[name]
                if param:
                    return param

            return None

        request['param'] = inner
        request['route'] = {'params': request.params}

    def get_param(self, param, default=None):
        return request.params.get(param, default)

    def get_trace_id(self) -> Optional[str]:
        """
        Returns traceId from request

        :returns: Returns traceId from request
        """
        trace_id = bottle.request.query.get('trace_id')
        if trace_id is None or trace_id == '':
            trace_id = bottle.request.headers.get('trace_id')
        return trace_id

    def register_route_with_auth(self, method: str, route: str, schema: Schema, authorize: Callable, action: Callable):
        """
        Registers an action with authorization in this objects REST server (service)
        by the given method and route.

        :param method: the HTTP method of the route.
        :param route: the route to register in this object's REST server (service).
        :param schema: the schema to use for parameter validation.
        :param authorize: the authorization interceptor
        :param action: the action to perform at the given route.
        """

        def action_with_authorize(*args, **kwargs):
            # hack to pass the parameters in authorizer
            bottle.request.params['kwargs'] = kwargs
            # bottle.request.params['args'] = args
            
            authorize()
            return next_action(*args, **kwargs)

        if authorize:
            next_action = action
            action = action_with_authorize

        self.register_route(method, route, schema, action)

    def register_interceptor(self, route: str, action: Callable):
        """
        Registers a middleware action for the given route.

        :param route: the route to register in this object's REST server (service).
        :param action: the middleware action to perform at the given route.
        """
        route = self.__fix_route(route)

        def intercept_handler():
            match = re.match('.*' + route, request.url) is not None
            if route is not None and route != '' and not match:
                pass
            else:
                return action()

        self.__service.add_hook('before_request', intercept_handler)
