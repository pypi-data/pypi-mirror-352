# -*- coding: utf-8 -*-
"""
    tests.rest.test_DummyCommandableHttpClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import time

from pip_services4_components.config import ConfigParams
from pip_services4_components.refer import References, Descriptor

from .DummyClientFixture import DummyClientFixture
from .DummyCommandableHttpClient import DummyCommandableHttpClient
from ..DummyService import DummyService
from ..controllers.DummyCommandableHttpController import DummyCommandableHttpController

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3001
)


class TestDummyCommandableHttpClient:
    fixture: DummyClientFixture
    controller: DummyCommandableHttpController
    client: DummyCommandableHttpClient

    @classmethod
    def setup_class(cls):
        service = DummyService()

        cls.controller = DummyCommandableHttpController()
        cls.controller.configure(rest_config)

        references = References.from_tuples(
            Descriptor("pip-services-dummies", "service", "default", "default", "1.0"), service,
            Descriptor("pip-services-dummies", "controller", "http", "default", "1.0"), cls.controller
        )

        cls.controller.set_references(references)

        cls.controller.open(None)

        time.sleep(0.5)

    @classmethod
    def teardown_class(cls):
        cls.controller.close(None)

    def setup_method(self):
        self.client = DummyCommandableHttpClient()
        self.fixture = DummyClientFixture(self.client)

        self.client.configure(rest_config)
        self.client.set_references(References())

        self.client.open(None)

    def teardown_method(self):
        self.client.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()
