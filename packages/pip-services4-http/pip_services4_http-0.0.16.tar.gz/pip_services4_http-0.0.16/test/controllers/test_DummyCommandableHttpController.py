# -*- coding: utf-8 -*-
"""
    test.controller.TestDummyCommandableHttpService
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy commandable HTTP service test

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json
import time

import requests
from pip_services4_components.config import ConfigParams
from pip_services4_components.refer import References, Descriptor
from pip_services4_components.context import IContext
from pip_services4_components.exec import Parameters
from pip_services4_data.query import DataPage

from .DummyCommandableHttpController import DummyCommandableHttpController
from ..Dummy import Dummy
from ..DummyService import DummyService
from ..SubDummy import SubDummy

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    "connection.host", "localhost",
    "connection.port", 3005,
    "swagger.enable", "true"
)

DUMMY1 = Dummy(None, 'Key 1', 'Content 1', [SubDummy('SubKey 1', 'SubContent 1')])
DUMMY2 = Dummy(None, 'Key 2', 'Content 2', [SubDummy('SubKey 2', 'SubContent 2')])


class TestDummyCommandableHttpController():
    srv: DummyService
    controller: DummyCommandableHttpController

    @classmethod
    def setup_class(cls):
        cls.srv = DummyService()

        cls.controller = DummyCommandableHttpController()
        cls.controller.configure(rest_config)

        references = References.from_tuples(
            Descriptor("pip-services-dummies", "service", "default", "default", "1.0"), cls.srv,
            Descriptor("pip-services-dummies", "controller", "http", "default", "1.0"), cls.controller
        )

        cls.controller.set_references(references)
        cls.controller.open(None)

    @classmethod
    def teardown_class(cls):
        cls.controller.close(None)

    def test_crud_operations(self):
        # Create one dummy
        response = self.invoke("/dummy/create_dummy", Parameters.from_tuples("dummy", DUMMY1.to_json()))

        dummy1 = Dummy.from_json(response)

        assert dummy1 is not None
        assert DUMMY1.key == dummy1.key
        assert DUMMY1.content == dummy1.content

        # Create another dummy
        response = self.invoke("/dummy/create_dummy", Parameters.from_tuples("dummy", DUMMY2.to_json()))

        dummy2 = Dummy.from_json(response)

        assert dummy2 is not None
        assert DUMMY2.key == dummy2.key
        assert DUMMY2.content == dummy2.content

        # Get all dummies
        response = self.invoke("/dummy/get_dummies", Parameters.from_tuples("dummies"))
        page = DataPage([Dummy.from_json(item) for item in response.get('data', [])], response.get('total'))

        assert page is not None
        assert 2 == len(page.data)

        # Update the dummy
        dummy1.content = "Updated Content 1"
        response = self.invoke("/dummy/update_dummy", Parameters.from_tuples("dummy", dummy1.to_json()))

        dummy = Dummy.from_json(response)

        assert dummy is not None
        assert dummy1.id == dummy.id
        assert dummy1.key == dummy.key
        assert "Updated Content 1" == dummy.content

        # Delete the dummy
        self.invoke("/dummy/delete_dummy", Parameters.from_tuples("dummy_id", dummy1.id))

        # Try to get deleted dummy
        get_dummy = self.invoke("/dummy/get_dummy_by_id", Parameters.from_tuples("dummy_id", dummy1.id))
        assert get_dummy is None

    def invoke(self, route, entity, headers=None):
        route = "http://localhost:3005" + route
        timeout = 5

        entity = {} if not entity else json.dumps(entity)

        # Call the service
        response = requests.request('POST', route, json=entity, timeout=timeout, headers=headers)
        if response.status_code != 204:
            return response.json()

    def test_check_trace_id(self):
        # check transmit trace_id over params
        result = self.invoke('/dummy/check_trace_id?trace_id=test_cor_id', None)
        assert 'test_cor_id' == result['trace_id']

        # check transmit trace_id over header
        headers = {'trace_id': "test_cor_id_header"}
        result = self.invoke('/dummy/check_trace_id', None, headers=headers)
        assert 'test_cor_id_header' == result['trace_id']

    def test_get_open_api_spec(self):
        response = requests.request('GET', 'http://localhost:3005/dummy/swagger')
        assert response.text.startswith('openapi:')

    def test_get_open_api_override(self):
        open_api_content = "swagger yaml content"

        # recreate service with new configuration
        self.controller.close(None)

        config = rest_config.set_defaults(ConfigParams.from_tuples("swagger.auto", False))

        service = DummyService()

        self.controller = DummyCommandableHttpController()
        self.controller.configure(config)

        references = References.from_tuples(
            Descriptor('pip-services-dummies', 'service', 'default', 'default', '1.0'), service,
            Descriptor('pip-services-dummies', 'controller', 'http', 'default', '1.0'), self.controller
        )
        self.controller.set_references(references)

        try:
            self.controller.open(None)

            response = requests.request('GET', 'http://localhost:3005/dummy/swagger')
            assert response.text == open_api_content
        finally:
            self.controller.close(None)
