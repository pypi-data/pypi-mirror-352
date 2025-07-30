# -*- coding: utf-8 -*-
"""
    pip_services4_http.clients.__init__
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Clients module initialization
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

__all__ = [ 'RestClient', 'CommandableHttpClient' ]

from .CommandableHttpClient import CommandableHttpClient
from .RestClient import RestClient
