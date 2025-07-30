# -*- coding: utf-8 -*-

import json
from abc import ABC
from typing import Optional, Any, Callable

import bottle
from pip_services4_commons.errors import BadRequestException, UnauthorizedException, NotFoundException, \
    ConflictException, UnknownException
from pip_services4_components.config import IConfigurable, ConfigParams
from pip_services4_components.refer import IReferenceable, DependencyResolver, IReferences
from pip_services4_data.query import FilterParams, PagingParams
from pip_services4_observability.count import CompositeCounters
from pip_services4_observability.log import CompositeLogger

from .HttpResponseSender import HttpResponseSender


class RestOperations(IConfigurable, IReferenceable, ABC):

    def __init__(self):
        super().__init__()
        self._logger: CompositeLogger = CompositeLogger()
        self._counters: CompositeCounters = CompositeCounters()
        self._dependency_resolver: DependencyResolver = DependencyResolver()

    def configure(self, config: ConfigParams):
        self._dependency_resolver.configure(config)

    def set_references(self, references: IReferences):
        self._logger.set_references(references)
        self._counters.set_references(references)
        self._dependency_resolver.set_references(references)

    def get_param(self, param, default=None):
        return bottle.request.params.get(param, default)

    def _get_trace_id(self) -> Optional[str]:
        """
        Returns traceId from request

        :returns: Returns traceId from request
        """
        trace_id = bottle.request.query.get('trace_id')
        if trace_id is None or trace_id == '':
            trace_id = bottle.request.headers.get('trace_id')

        return trace_id

    def _get_filter_params(self) -> FilterParams:
        data = dict(bottle.request.query.decode())
        data.pop('trace_id', None)
        data.pop('skip', None)
        data.pop('take', None)
        data.pop('total', None)
        return FilterParams(data)

    def _get_paging_params(self) -> PagingParams:
        params = dict(bottle.request.query.decode())
        skip = params.get('skip')
        take = params.get('take')
        total = params.get('total')
        return PagingParams(skip, take, total)

    def _get_data(self) -> Optional[str]:
        data = bottle.request.json
        if isinstance(data, str):
            return json.loads(bottle.request.json)
        elif bottle.request.json:
            return bottle.request.json
        else:
            return None

    def _send_result(self, result: Any = None) -> Optional[str]:
        return HttpResponseSender.send_result(result)

    def _send_empty_result(self, result: Any = None) -> Optional[str]:
        return HttpResponseSender.send_empty_result(result)

    def _send_created_result(self, result: Any = None) -> Optional[str]:
        return HttpResponseSender.send_created_result(result)

    def _send_deleted_result(self, result: Any = None) -> Optional[str]:
        return HttpResponseSender.send_deleted_result(result)

    def _send_error(self, error: Any = None) -> str:
        return HttpResponseSender.send_error(error)

    def _send_bad_request(self, message: str) -> str:
        trace_id = self._get_trace_id()
        error = BadRequestException(trace_id, 'BAD_REQUEST', message)
        return self._send_error(error)

    def _send_unauthorized(self, message: str) -> str:
        trace_id = self._get_trace_id()
        error = UnauthorizedException(trace_id, 'UNAUTHORIZED', message)
        return self._send_error(error)

    def _send_not_found(self, message: str) -> str:
        trace_id = self._get_trace_id()
        error = NotFoundException(trace_id, 'NOT_FOUND', message)
        return self._send_error(error)

    def _send_conflict(self, message: str) -> str:
        trace_id = self._get_trace_id()
        error = ConflictException(trace_id, 'CONFLICT', message)
        return self._send_error(error)

    def _send_session_expired(self, message: str) -> str:
        trace_id = self._get_trace_id()
        error = UnknownException(trace_id, 'SESSION_EXPIRED', message)
        error.status = 440
        return self._send_error(error)

    def _send_internal_error(self, message: str) -> str:
        trace_id = self._get_trace_id()
        error = UnknownException(trace_id, 'INTERNAL', message)
        return self._send_error(error)

    def _send_server_unavailable(self, message: str) -> str:
        trace_id = self._get_trace_id()
        error = ConflictException(trace_id, 'SERVER_UNAVAILABLE', message)
        error.status = 503
        return self._send_error(error)

    def invoke(self, operation: str) -> Callable:
        for attr in dir(self):
            if attr in dir(self):
                return lambda param=None: getattr(self, operation)(param)
