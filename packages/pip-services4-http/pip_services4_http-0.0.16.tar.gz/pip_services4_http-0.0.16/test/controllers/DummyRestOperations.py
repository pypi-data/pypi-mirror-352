# -*- coding: utf-8 -*-
"""
    test.rest.DummyRestController
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy REST service
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC

from pip_services4_commons.errors import UnsupportedException
from pip_services4_components.refer import Descriptor

from pip_services4_http.controller import RestOperations


class DummyRestOperations(RestOperations, ABC):

    _service = None

    def __init__(self):
        super(DummyRestOperations, self).__init__()
        self._dependency_resolver.put('service', Descriptor('pip-services-dummies', 'service', 'default', '*', '*'))

    def set_references(self, references):
        super(DummyRestOperations, self).set_references(references)
        self._service = self._dependency_resolver.get_one_required('service')

    def get_page_by_filter(self):
        trace_id = self._get_trace_id()
        filters = self._get_filter_params()
        paging = self._get_paging_params()
        return self._send_result(self._service.get_page_by_filter(trace_id, filters, paging))

    def get_one_by_id(self, id):
        trace_id = self._get_trace_id()
        return self._send_result(self._service.get_one_by_id(trace_id, id))

    def create(self):
        trace_id = self._get_trace_id()
        entity = self._get_data()
        return self._send_created_result(self._service.create(trace_id, entity))

    def update(self, id):
        trace_id = self._get_trace_id()
        entity = self._get_data()
        return self._send_result(self._service.update(trace_id, entity))

    def delete_by_id(self, id):
        trace_id = self._get_trace_id()
        self._service.delete_by_id(trace_id, id)
        return self._send_deleted_result()

    def handled_error(self):
        raise UnsupportedException('NotSupported', 'Test handled error')

    def unhandled_error(self):
        raise TypeError('Test unhandled error')

    def send_bad_request(self, message):
        return self._send_bad_request(message)

 
