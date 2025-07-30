# -*- coding: utf-8 -*-
"""
    tests.rest.test_DummyRestClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from pip_services4_components.config import ConfigParams
from pip_services4_components.refer import References, Descriptor

from .DummyClientFixture import DummyClientFixture
from .DummyRestClient import DummyRestClient
from ..DummyService import DummyService
from ..controllers.DummyRestController import DummyRestController

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3000,
    "options.trace_id_place", "headers",
)


class TestDummyRestClient:
    fixture = None
    controller = None
    client = None

    @classmethod
    def setup_class(cls):
        service = DummyService()

        cls.controller = DummyRestController()
        cls.controller.configure(rest_config)

        references = References.from_tuples(
            Descriptor("pip-services-dummies", "service", "default", "default", "1.0"), service,
            Descriptor("pip-services-dummies", "controller", "rest", "default", "1.0"), cls.controller,
        )

        cls.controller.set_references(references)

        cls.controller.open(None)

    def teardown_class(self):
        self.controller.close(None)

    def setup_method(self):
        self.client = DummyRestClient()
        self.fixture = DummyClientFixture(self.client)

        self.client.configure(rest_config)
        self.client.set_references(References())

        self.client.open(None)

    def teardown_method(self, method):
        self.client.close(None)

    def test_crud_operations(self):
        self.fixture.test_crud_operations()
