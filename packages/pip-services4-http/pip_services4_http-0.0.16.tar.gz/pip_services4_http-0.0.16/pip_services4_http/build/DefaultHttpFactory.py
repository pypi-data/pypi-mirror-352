# -*- coding: utf-8 -*-
"""
    pip_services4_http.build.DefaultHttpFactory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    DefaultHttpFactory implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from pip_services4_components.build import Factory
from pip_services4_components.refer import Descriptor

from ..controller import HttpEndpoint, StatusRestController, HeartbeatRestController


class DefaultHttpFactory(Factory):
    """
    Creates Http components by their descriptors.
    """

    HttpEndpointDescriptor = Descriptor("pip-services", "endpoint", "http", "*", "1.0")
    StatusServiceDescriptor = Descriptor("pip-services", "status-controller", "http", "*", "1.0")
    HeartbeatServiceDescriptor = Descriptor("pip-services", "heartbeat-controller", "http", "*", "1.0")

    def __init__(self):
        """
        Create a new instance of the factory.
        """
        super(DefaultHttpFactory, self).__init__()
        self.register_as_type(self.HttpEndpointDescriptor, HttpEndpoint)
        self.register_as_type(self.StatusServiceDescriptor, StatusRestController)
        self.register_as_type(self.HeartbeatServiceDescriptor, HeartbeatRestController)
