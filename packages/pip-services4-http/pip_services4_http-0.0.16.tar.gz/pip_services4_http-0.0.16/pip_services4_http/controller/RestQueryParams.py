# -*- coding: utf-8 -*-
"""
    pip_services4_http.controller.RestQueryParams
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    REST query parameters implementation
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services4_data.keys import IdGenerator
from pip_services4_data.query import FilterParams, PagingParams


class RestQueryParams(dict):

    def __init__(self, trace_id: Optional[str] = None, filte: FilterParams = None, paging: PagingParams = None):
        super().__init__()
        self.add_trace_id(trace_id)
        self.add_filter_params(filte)
        self.add_paging_params(paging)

    def add_trace_id(self, trace_id: Optional[str]=None):
        # Automatically generate short ids for now
        if trace_id is None:
            trace_id = IdGenerator.next_short()

        self['trace_id'] = trace_id

    def add_filter_params(self, filter):
        if filter is None: return

        for key, value in filter.items():
            self[key] = value

    def add_paging_params(self, paging: PagingParams):
        if paging is None: return

        if not (paging.total is None):
            self['total'] = paging.total
        if not (paging.skip is None):
            self['skip'] = paging.skip
        if not (paging.take is None):
            self['take'] = paging.take
