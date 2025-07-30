# -*- coding: utf-8 -*-
"""
    test_DummyRestController
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy commandable HTTP service test

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json
import os

import requests
from pip_services4_components.config import ConfigParams
from pip_services4_components.refer import References, Descriptor
from pip_services4_data.keys import IdGenerator
from pip_services4_data.query import DataPage

from ..Dummy import Dummy
from ..DummyService import DummyService
from ..SubDummy import SubDummy
from ..controllers.DummyRestController import DummyRestController

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    "connection.host", "localhost",
    "connection.port", 3001,
    "swagger.content", "swagger yaml or json content",  # for test only
    "swagger.enable", "true"
)

DUMMY1 = Dummy(None, 'Key 1', 'Content 1', [SubDummy('SubKey 1', 'SubContent 1')])
DUMMY2 = Dummy(None, 'Key 2', 'Content 2', [SubDummy('SubKey 2', 'SubContent 2')])


class TestDummyRestController:
    srv = None
    controller = None

    @classmethod
    def setup_class(cls):
        cls.srv = DummyService()

        cls.controller = DummyRestController()
        cls.controller.configure(rest_config)

        references = References.from_tuples(
            Descriptor("pip-services-dummies", "service", "default", "default", "1.0"), cls.srv,
            Descriptor("pip-services-dummies", "controller", "http", "default", "1.0"), cls.controller
        )

        cls.controller.set_references(references)
        cls.controller.open(None)

    # def setup_class(cls, method):

    @classmethod
    def teardown_class(cls):
        cls.controller.close(None)

    def test_crud_operations(self):
        # Create one dummy
        response = self.invoke('POST', "/dummies", DUMMY1.to_json())

        dummy1 = Dummy.from_json(response)
        assert dummy1 is not None
        assert DUMMY1.key == dummy1.key
        assert DUMMY1.content == dummy1.content

        # Create another dummy
        response = self.invoke('POST', "/dummies", DUMMY2.to_json())

        dummy2 = Dummy.from_json(response)

        assert dummy2 is not None
        assert DUMMY2.key == dummy2.key
        assert DUMMY2.content == dummy2.content

        # Get all dummies
        response = self.invoke('GET', '/dummies', None)
        page = DataPage([Dummy.from_json(item) for item in response.get('data', [])], response.get('total'))
        assert page is not None
        assert len(page.data) == 2

        # Update the dummy
        dummy1.content = 'Updated Content 1'
        response = self.invoke('PUT', '/dummies', dummy1.to_json())

        dummy = Dummy(**response)

        assert dummy.content == 'Updated Content 1'
        assert dummy.key == dummy1.key

        dummy1 = dummy

        # Delete dummy
        self.invoke('DELETE', f'/dummies/{dummy1.id}')

        # Try to get delete dummy
        response = self.invoke('GET', f'/dummies/{dummy1.id}')

        assert response is None

        assert 4 == self.controller.get_number_of_calls()

    def test_check_trace_id(self):
        # check transmit trace_id over params
        result = self.invoke('GET', '/dummies/check/trace_id?trace_id=test_cor_id')
        assert 'test_cor_id' == result['trace_id']

        # check transmit trace_id over header
        result = self.invoke('GET', '/dummies/check/trace_id', headers={"trace_id": "test_cor_id_header"})
        assert 'test_cor_id_header' == result['trace_id']

    def invoke(self, method, route, entity=None, headers=None):
        route = "http://localhost:3001" + route

        # Call the service
        if entity:
            entity = json.dumps(entity)
        response = requests.request(method, route, json=entity, timeout=5, headers=headers)
        if response.status_code != 204:
            return response.json()

    def test_get_open_api_spec_from_string(self):
        response = requests.request('GET', 'http://localhost:3001/swagger')

        open_api_content = rest_config.get_as_string('swagger.content')
        assert open_api_content == response.text

    def test_get_open_api_spec_from_file(self):
        self.controller.close(None)

        open_api_content = 'swagger yaml content from file'
        filename = 'dummy_' + IdGenerator.next_long() + '.tmp'

        # create temp file
        with open(filename, 'w') as f:
            f.write(open_api_content)

        # recreate service with new configuration
        service_config = ConfigParams.from_tuples(
            "connection.protocol", "http",
            "connection.host", "localhost",
            "connection.port", 3001,
            "swagger.path", filename,  # for test only
            "swagger.enable", "true"
        )
        ctrl = DummyService()

        self.controller = DummyRestController()
        self.controller.configure(service_config)

        references = References.from_tuples(
            Descriptor('pip-services-dummies', 'service', 'default', 'default', '1.0'), ctrl,
            Descriptor('pip-services-dummies', 'controller', 'rest', 'default', '1.0'), self.controller
        )
        self.controller.set_references(references)

        self.controller.open(None)

        response = requests.request('GET', 'http://localhost:3001/swagger')
        assert response.text == open_api_content

        # delete temp file
        os.remove(filename)
