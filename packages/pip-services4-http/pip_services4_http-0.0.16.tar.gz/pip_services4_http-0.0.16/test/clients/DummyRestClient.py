# -*- coding: utf-8 -*-
"""
    test.rest.DummyRestClient
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Dummy REST client implementation
    
    :copyright: Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from typing import Optional

from pip_services4_components.context import IContext
from pip_services4_data.query import FilterParams, PagingParams, DataPage

from pip_services4_http.clients import RestClient
from .IDummyClient import IDummyClient
from .. import Dummy


class DummyRestClient(RestClient, IDummyClient):

    def __init__(self):
        super(DummyRestClient, self).__init__()

    def get_page_by_filter(self, context, filters: FilterParams, paging: PagingParams) -> DataPage:
        params = {}
        self._add_filter_params(params, filters)
        self._add_paging_params(params, paging)

        timing = self._instrument(context, 'dummy.get_page_by_filter')
        try:
            result = self._call(
                'GET',
                '/dummies',
                context,
                params
            )

            page = DataPage(
                data=[Dummy.from_json(item) for item in result['data']],
                total=result['total']
            )
            return page
        except Exception as err:
            timing.end_timing(err)
            raise err
        finally:
            timing.end_success()

    def get_one_by_id(self, context, dummy_id):
        timing = self._instrument(context, 'dummy.get_one_by_id')
        try:
            response = self._call(
                'GET',
                f'/dummies/{dummy_id}',
                context,
            )
            if response:
                return Dummy.from_json(response)
        except Exception as err:
            timing.end_timing(err)
            raise err
        finally:
            timing.end_success()

    def create(self, context, entity):
        timing = self._instrument(context, 'dummy.create')
        try:
            response = self._call(
                'POST',
                '/dummies',
                context,
                None,
                entity
            )
            if response:
                return Dummy.from_json(response)
        except Exception as err:
            timing.end_timing(err)
            raise err
        finally:
            timing.end_success()

    def update(self, context, entity):
        timing = self._instrument(context, 'dummy.update')
        try:
            response = self._call(
                'PUT',
                '/dummies',
                context,
                None,
                entity
            )
            if response:
                return Dummy.from_json(response)
        except Exception as err:
            timing.end_timing(err)
            raise err
        finally:
            timing.end_success()

    def delete_by_id(self, context: Optional[IContext], dummy_id: str) -> Dummy:
        timing = self._instrument(context, 'dummy.delete_by_id')
        try:
            response = self._call(
                'DELETE',
                f'/dummies/{dummy_id}',
                context,
                None
            )
            if response:
                return Dummy.from_json(response)
        except Exception as err:
            timing.end_timing(err)
            raise err
        finally:
            timing.end_success()

    def check_trace_id(self, context: Optional[IContext]) -> str:
        timing = self._instrument(context, 'dummy.check_trace_id')
        try:
            result = self._call(
                'get',
                f'/dummies/check/trace_id',
                context,
                None
            )
            return None if not result else result.get('trace_id')
        except Exception as err:
            timing.end_timing(err)
            raise err
        finally:
            timing.end_success()
