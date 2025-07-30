# -*- coding: utf-8 -*-
"""
    test.rest.DummyCommandableHttpClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy commandable HTTP client
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional


from pip_services4_components.context import IContext
from pip_services4_data.query import FilterParams, PagingParams, DataPage

from pip_services4_http.clients import CommandableHttpClient
from .IDummyClient import IDummyClient
from .. import Dummy


class DummyCommandableHttpClient(CommandableHttpClient, IDummyClient):

    def __init__(self):
        super(DummyCommandableHttpClient, self).__init__('dummy')

    def get_page_by_filter(self, context: Optional[IContext], filter: FilterParams, paging: PagingParams) -> DataPage:
        result = self.call_command(
            'get_dummies',
            context,
            {
                'filter': filter,
                'paging': paging
            }
        )
        page = DataPage(
            data=[Dummy.from_json(item) for item in result['data']],
            total=result['total']
        )
        return page

    def get_one_by_id(self, context: Optional[IContext], dummy_id: str) -> Dummy:
        response = self.call_command(
            'get_dummy_by_id',
            context,
            {
                'dummy_id': dummy_id
            }
        )
        if response:
            return Dummy.from_json(response)

    def create(self, context: Optional[IContext], item: Dummy) -> Dummy:
        response = self.call_command(
            'create_dummy',
            context,
            {
                'dummy': item
            }
        )
        if response:
            return Dummy.from_json(response)

    def update(self, context: Optional[IContext], item: Dummy) -> Dummy:
        response = self.call_command(
            'update_dummy',
            context,
            {
                'dummy': item
            }
        )
        if response:
            return Dummy.from_json(response)

    def delete_by_id(self, context: Optional[IContext], dummy_id: str) -> Dummy:
        response = self.call_command(
            'delete_dummy',
            context,
            {
                'dummy_id': dummy_id
            }
        )
        if response:
            return Dummy.from_json(response)

    def check_trace_id(self, context: Optional[IContext]) -> str:
        result = self.call_command(
            'check_trace_id',
            context,
            {}
        )
        return None if not result else result.get('trace_id')
