# -*- coding: utf-8 -*-
"""
    test_DummyRestController
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy commandable HTTP service test

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import requests
from pip_services4_components.config import ConfigParams
from pip_services4_components.context import ContextInfo
from pip_services4_components.refer import References, Descriptor

from pip_services4_http.controller import StatusRestController

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3002
)


class TestStatusRestController():
    controller = None

    @classmethod
    def setup_class(cls):
        cls.controller = StatusRestController()
        cls.controller.configure(rest_config)

        contextInfo = ContextInfo()
        contextInfo.name = "Test"
        contextInfo.description = "This is a test container"

        references = References.from_tuples(
            Descriptor("pip-services", "context-info", "default", "default", "1.0"), contextInfo,
            Descriptor("pip-services-dummies", "controller", "http", "default", "1.0"), cls.controller
        )

        cls.controller.set_references(references)

    def setup_method(self, method):
        self.controller.open(None)

    def teardown_method(self, method):
        self.controller.close(None)

    def test_status(self):
        result = self.invoke("/status")

        assert result.text is not None

    def invoke(self, route):
        params = {}
        route = "http://localhost:3002" + route
        response = None
        timeout = 5

        # Call the service
        response = requests.request('GET', route, params=params, timeout=timeout)
        return response
