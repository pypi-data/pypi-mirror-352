# -*- coding: utf-8 -*-
"""
    test_DummyRestController
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dummy commandable HTTP service test

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
import json

import requests
from pip_services4_components.config import ConfigParams
from pip_services4_components.refer import References, Descriptor

from pip_services4_http.controller import HttpEndpoint
from ..Dummy import Dummy
from ..DummyService import DummyService
from ..SubDummy import SubDummy
from ..controllers.DummyRestController import DummyRestController

DUMMY1 = Dummy(None, 'Key 1', 'Content 1', [SubDummy('SubKey 1', 'SubContent 1')])
DUMMY2 = Dummy(None, 'Key 2', 'Content 2', [SubDummy('SubKey 2', 'SubContent 2')])

rest_config = ConfigParams.from_tuples(
    "connection.protocol", "http",
    'connection.host', 'localhost',
    'connection.port', 3004
)


class TestHttpEndpointController():
    controller = None
    endpoint = None

    @classmethod
    def setup_class(cls):
        service = DummyService()
        cls.controller = DummyRestController()
        cls.controller.configure(ConfigParams.from_tuples(
            'base_route', '/api/v1'
        ))

        cls.endpoint = HttpEndpoint()
        cls.endpoint.configure(rest_config)

        references = References.from_tuples(
            Descriptor("pip-services-dummies", "service", "default", "default", "1.0"), service,
            Descriptor('pip-services-dummies', 'controller', 'rest', 'default', '1.0'), cls.controller,
            Descriptor('pip-services', 'endpoint', 'http', 'default', '1.0'), cls.endpoint
        )

        cls.controller.set_references(references)
        cls.endpoint.open(None)
        cls.controller.open(None)

    def teardown_method(self):
        self.controller.close(None)
        self.endpoint.close(None)

    def test_crud_operations(self):
        response = self.invoke("/api/v1/dummies", DUMMY1.to_json(), "POST")

        dummy1 = Dummy(**response.json())

        assert dummy1 is not None
        assert DUMMY1.key == dummy1.key
        assert DUMMY1.content == dummy1.content

        response = self.invoke("/api/v1/dummies/"+str(dummy1.id), str(dummy1.id), "GET")
        
        dummy1 = Dummy(**response.json())

        assert dummy1 is not None
        assert DUMMY1.key == dummy1.key
        assert DUMMY1.content == dummy1.content


    def invoke(self, route, entity, method):
        route = "http://localhost:3004" + route

        # Call the service
        data = json.dumps(entity)
        response = requests.request(method, route, json=data, timeout=5)
        return response
