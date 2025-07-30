# -*- coding: utf-8 -*-
"""
    pip_services4_http.controller.CommandableHttpController
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Commandable HTTP service implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Callable

from pip_services4_components.config import ConfigParams
from pip_services4_components.context import Context
from pip_services4_rpc.commands import CommandSet, ICommand, ICommandable
from pip_services4_components.exec import Parameters

from .CommandableSwaggerDocument import CommandableSwaggerDocument
from .RestController import RestController


class CommandableHttpController(RestController):
    """
    Abstract controller that receives remove calls via HTTP/REST protocol to operations automatically generated for commands defined in ICommandable components. Each command is exposed as POST operation that receives all parameters in body object. Commandable controller require only 3 lines of code to implement a robust external HTTP-based remote interface.

    ### Configuration parameters ###
        - base_route:              base route for remote URI
        - dependencies:
            - endpoint:              override for HTTP Endpoint dependency
            - service:            override for Service dependency
        - connection(s):
            - discovery_key:         (optional) a key to retrieve the connection from IDiscovery
            - protocol:              connection protocol: http or https
            - host:                  host name or IP address
            - port:                  port number
            - uri:                   resource URI or connection string with all parameters in it

    ### References ###
        - `*:logger:*:*:1.0`           (optional) :class:`ILogger <pip_services4_observability.log.ILogger.ILogger>` components to pass log messages
        - `*:counters:*:*:1.0`         (optional) :class:`ICounters <pip_services4_observability.count.ICounters.ICounters>` components to pass collected measurements
        - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services4_config.connect.IDiscovery.IDiscovery>` controller to resolve connection
        - `*:endpoint:http:*:1.0`      (optional) :class:`HttpEndpoint <pip_services4_http.controller.HttpEndpoint` reference

    Example:

    .. code-block:: python

          class MyCommandableHttpController(CommandableHttpController):
              def __init__(self):
                  super(MyCommandableHttpController, self).__init__()
                  self._dependencyResolver.put("service", Descriptor("mygroup","service","*","*","1.0"))

              # ...

          controller = MyCommandableHttpController()
          controller.configure(ConfigParams.from_tuples("connection.protocol", "http",
                                                    "connection.host", "localhost",
                                                    "connection.port", 8080))
          controller.set_references(References.from_tuples(Descriptor("mygroup","service","default","default","1.0"), service))
          controller.open("123")
          # ...
    """

    def __init__(self, base_route: str):
        """
        Creates a new instance of the service.

        :param base_route: a service base route.
        """
        super(CommandableHttpController, self).__init__()
        self._command_set: CommandSet = None
        self._swagger_auto: bool = True

        self._base_route = base_route
        self._dependency_resolver.put('service', 'none')

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.

        :param config: configuration parameters to be set.
        """
        super().configure(config)

        self._swagger_auto = config.get_as_boolean_with_default('swagger.auto', self._swagger_auto)

    def __get_handler(self, command: ICommand) -> Callable:
        def handler():
            params = self._get_data()
            trace_id = self._get_trace_id()
            args = Parameters.from_value(params)
            timing = self._instrument(trace_id, self._base_route + '.' + command.get_name())
            try:
                result = command.execute(Context.from_trace_id(trace_id), args)
                return self.send_result(result)
            finally:
                timing.end_timing()

        return handler

    def register(self):
        """
        Registers all service routes in HTTP endpoint.
        """
        service = self._dependency_resolver.get_one_required('service')
        if not isinstance(service, ICommandable):
            raise Exception("Service has to implement ICommandable interface")
        self._command_set = service.get_command_set()
        commands = self._command_set.get_commands()
        for command in commands:
            route = self.fix_route(command.get_name())
            # if route[0] != '/':
            #     route = '/' + route #self._base_route + '/' + command.get_name()

            self.register_route('POST', route, None, self.__get_handler(command))

        if self._swagger_auto:
            swagger_config = self._config.get_section('swagger')

            doc = CommandableSwaggerDocument(self._base_route, swagger_config, commands)
            self._register_open_api_spec(doc.to_string())
