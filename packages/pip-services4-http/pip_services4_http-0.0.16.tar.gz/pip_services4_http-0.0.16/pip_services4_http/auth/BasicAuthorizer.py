# -*- coding: utf-8 -*-
from typing import Callable

import bottle
from pip_services4_commons.errors import UnauthorizedException

from pip_services4_http.controller.HttpResponseSender import HttpResponseSender
from bottle import abort


class BasicAuthorizer:

    def anybody(self) -> Callable:
        return lambda: None

    def signed(self) -> Callable:
        def inner():
            user = bottle.request.environ.get('bottle.request.ext.user')
            if user is None:
                raise UnauthorizedException(
                    None,
                    'NOT_SIGNED',
                    'User must be signed in to perform this operation '
                ).with_status(401)
        return inner
