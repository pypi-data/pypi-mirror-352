# -*- coding: utf-8 -*-
"""
    pip_services4_http.clients.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Clients module implementation

    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = ['DummyCommandableHttpController', 'DummyRestController']

from .DummyCommandableHttpController import DummyCommandableHttpController
from .DummyRestController import DummyRestController
from .DummyRestOperations import DummyRestOperations