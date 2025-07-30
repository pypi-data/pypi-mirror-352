# -*- coding: utf-8 -*-

import datetime
import json

import requests
from pip_services4_components.config import ConfigParams

from pip_services4_http.controller.HeartbeatRestController import HeartbeatRestController

rest_config = ConfigParams.from_tuples(
    'connection.protocol', 'http',
    'connection.host', 'localhost',
    'connection.port', 3003
)


class TestHeartBeatRestController:
    service = None
    rest = None

    @classmethod
    def setup_class(cls):
        cls.service = HeartbeatRestController()
        cls.service.configure(rest_config)

    def setup_method(self, method):
        self.service.open(None)

    def teardown_method(self, method):
        self.service.close(None)

    def test_status(self):
        res = self.invoke()
        assert type(res) is not Exception
        assert type(datetime.datetime.strptime(res, '%Y-%m-%dT%H:%M:%S.%fZ')) == datetime.datetime

    def invoke(self, route='/heartbeat', entity=None):
        params = {}
        route = "http://localhost:3003" + route
        response = None
        timeout = 5

        # Call the service
        data = json.dumps(entity)
        response = requests.request('GET', route, params=params, json=data, timeout=timeout)
        return response.json()
