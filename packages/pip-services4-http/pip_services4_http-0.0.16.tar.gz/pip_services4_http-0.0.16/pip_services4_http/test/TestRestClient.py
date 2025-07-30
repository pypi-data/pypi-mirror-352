# -*- coding: utf-8 -*-
from typing import Any, Optional

from pip_services4_http.clients import RestClient
from pip_services4_components.context import IContext

class TestRestClient(RestClient):
    """
    REST client used for automated testing.
    """

    def __init__(self, base_route: str):
        super(TestRestClient, self).__init__()
        self._base_route = base_route

    def _call(self, method: str, route: str, context: Optional[IContext] = None, params: Any = None,
              data: Any = None) -> Any:
        """
        Calls a remote method via HTTP/REST protocol.

        :param method: HTTP method: "get", "head", "post", "put", "delete"
        :param route: a command route. Base route will be added to this route
        :param context: (optional) transaction id to trace execution through call chain.
        :param params: (optional) query parameters.
        :param data: (optional) body object.
        :returns: a result object.
        """
        return super(TestRestClient, self)._call(method, route, context, params, data)
