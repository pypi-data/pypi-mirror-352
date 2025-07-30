# -*- coding: utf-8 -*-
"""
    pip_services4_http.connect.HttpConnectionResolver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    HttpConnectionResolver implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional, List
from urllib.parse import urlparse

from pip_services4_commons.errors import ConfigException
from pip_services4_components.config import IConfigurable, ConfigParams
from pip_services4_components.context import IContext
from pip_services4_components.refer import IReferenceable, IReferences
from pip_services4_config.auth import CredentialResolver, CredentialParams
from pip_services4_config.connect import ConnectionResolver, ConnectionParams


class HttpConnectionResolver(IReferenceable, IConfigurable):
    """
    Helper class to retrieve connections for HTTP-based controller abd clients. In addition to regular functions of
    ConnectionResolver is able to parse http:// URIs and validate connection parameters before returning them.

    ### Configuration parameters ###
        - connection:
            - discovery_key:               (optional) a key to retrieve the connection from IDiscovery
            - ...                          other connection parameters
        - connections:                   alternative to connection
            - [connection params 1]:       first connection parameters
            -  ...
            - [connection params N]:       Nth connection parameters
            -  ...

    ### References ###
        - `*:discovery:*:*:1.0`        (optional) :class:`IDiscovery <pip_services4_config.connect.IDiscovery.IDiscovery>` controller to resolve connection

    Example:
    
    .. code-block:: python

          config = ConfigParams.from_tuples("connection.host", "10.1.1.100","connection.port", 8080)
          connectionResolver = HttpConnectionResolver()
          connectionResolver.configure(config)
          connectionResolver.set_references(references)
          params = connectionResolver.resolve("123")
    """

    def __init__(self):
        # # Create connection resolver.
        self._connection_resolver: ConnectionResolver = ConnectionResolver()
        # # The base credential resolver.
        self._credential_resolver: CredentialResolver = CredentialResolver()

    def configure(self, config: ConfigParams):
        """
        Configures component by passing configuration parameters.
        :param config: configuration parameters to be set.
        """
        self._connection_resolver.configure(config)
        self._credential_resolver.configure(config)

    def set_references(self, references: IReferences):
        """
        Sets references to dependent components.

        :param references: references to locate the component dependencies.
        """
        self._connection_resolver.set_references(references)
        self._credential_resolver.set_references(references)

    def __validate_connection(self, context: Optional[IContext], connection: ConnectionParams,
                              credential: CredentialParams = None):

        # Sometimes when we use https we are on an internal network and do not want to have to deal with security.
        # When we need a https connection and we don't want to pass credentials, flag is 'credential.internal_network',
        # this flag just has to be present and non null for this functionality to work.
        if connection is None:
            raise ConfigException(context, "NO_CONNECTION", "HTTP connection is not set")
        uri = connection.get_as_string('uri')

        if uri is not None:
            return None

        protocol = connection.get_protocol_with_default("http")
        if protocol != "http" and 'https' != protocol:
            raise ConfigException(context,
                                  "WRONG_PROTOCOL",
                                  "Protocol is not supported by REST connection") \
                .with_details("protocol", protocol)

        host = connection.get_as_string('host')
        if host is None:
            raise ConfigException(context, "NO_HOST", "Connection host is not set")

        port = connection.get_as_integer('port')
        if port == 0:
            raise ConfigException(context, "NO_PORT", "Connection port is not set")

        # Check HTTPS credentials
        if protocol == 'https':
            # Check for credential
            if credential is None or credential.length() == 0:
                raise ConfigException(
                    context, 'NO_CREDENTIAL',
                    'SSL certificates are not configured for HTTPS protocol')
            else:
                # Sometimes when we use https we are on an internal network and do not want to have to deal with
                # security. When we need a https connection and we don't want to pass credentials,
                # flag is 'credential.internal_network', this flag just has to be present and non null for this
                # functionality to work.
                if credential.get_as_nullable_string('internal_network') is None:
                    if credential.get_as_nullable_string('ssl_key_file') is None:
                        raise ConfigException(
                            context, 'NO_SSL_KEY_FILE',
                            'SSL key file is not configured in credentials')
                    elif credential.get_as_nullable_string('ssl_crt_file') is None:
                        raise ConfigException(
                            context, 'NO_SSL_CRT_FILE',
                            'SSL crt file is not configured in credentials')
        return None

    def __compose_connection(self, connections: List[ConnectionParams],
                             credential: CredentialParams = None) -> ConfigParams:
        connection = ConfigParams.merge_configs(*connections)

        uri = connection.get_as_string('uri')

        if uri is None or uri == "":

            protocol = connection.get_as_string_with_default('protocol', "uri")
            host = connection.get_as_string('host')
            port = connection.get_as_integer('port')

            uri = protocol + "://" + host if host else None
            if port != 0:
                uri = uri + ":" + str(port)
            connection.set_as_object('uri', uri)

        else:
            address = urlparse(uri)

            connection.set_as_object('protocol', address.scheme)
            connection.set_as_object('host', address.hostname)
            connection.set_as_object('port', address.port)

        if connection.get_as_string('protocol') == 'https':
            if credential.get_as_nullable_string('internal_network') is None:
                connection = connection.override(credential)

        return connection

    def resolve(self, context: Optional[IContext]) -> ConfigParams:
        """
        Resolves a single component connection. If connections are configured to be retrieved from Discovery service
        it finds a IDiscovery and resolves the connection there.

        :param context: (optional) transaction id to trace execution through call chain.

        :return: resolved connection.
        """

        connection = self._connection_resolver.resolve(context)
        credential = self._credential_resolver.lookup(context)
        self.__validate_connection(context, connection, credential)
        return self.__compose_connection([connection], credential)

    def resolve_all(self, context: Optional[IContext]) -> ConfigParams:
        """
        Resolves all component connection. If connections are configured to be retrieved from Discovery service it finds a IDiscovery and resolves the connection there.

        :param context: (optional) transaction id to trace execution through call chain.

        :return: resolved connections.
        """

        connections = self._connection_resolver.resolve_all(context)
        credential = self._credential_resolver.lookup(context)

        connections = connections or []

        for connection in connections:
            self.__validate_connection(context, connection, credential)

        return self.__compose_connection(connections, credential)

    def register(self, context: Optional[IContext]):
        """
        Registers the given connection in all referenced discovery controller. This method can be used for dynamic service discovery.

        :param context: (optional) transaction id to trace execution through call chain.
        """
        connection = self._connection_resolver.resolve(context)
        credential = self._credential_resolver.lookup(context)
        self.__validate_connection(context, connection, credential)
        self._connection_resolver.register(context, connection)
