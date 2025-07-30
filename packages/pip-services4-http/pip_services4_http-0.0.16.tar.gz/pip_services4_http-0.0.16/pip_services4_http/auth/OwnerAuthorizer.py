# -*- coding: utf-8 -*-
from typing import Callable

import bottle
from pip_services4_commons.errors import UnauthorizedException

from pip_services4_http.controller.HttpResponseSender import HttpResponseSender


class OwnerAuthorizer:

    def owner(self, id_param: str = 'user_id') -> Callable:
        def inner():
            user = bottle.request.environ.get('bottle.request.ext.user')
            if user is None:
                raise UnauthorizedException(
                    None,
                    'NOT_SIGNED',
                    'User must be signed in to perform this operation'
                ).with_status(401)
            else:
                user_id = dict(bottle.request.query.decode()).get(id_param)
                if bottle.request.environ.get('bottle.request.ext.user') != user_id:
                    raise UnauthorizedException(
                        None,
                        'FORBIDDEN',
                        'Only data owner can perform this operation'
                    ).with_status(403)

        return inner

    def owner_or_admin(self, id_param: str = 'user_id') -> Callable:
        def inner():
            user = bottle.request.environ.get('bottle.request.ext.user')
            if user is None:
                raise UnauthorizedException(
                    None,
                    'NOT_SIGNED',
                    'User must be signed in to perform this operation'
                ).with_status(401)
            user_id = bottle.request.environ.get('bottle.request.ext.' + id_param)

            roles = user.get('roles') if isinstance(user, dict) else None
            is_admin = roles and 'admin' in roles

            if str(user.get('id')) != str(user_id) and not is_admin:
                    raise UnauthorizedException(
                        None,
                        'FORBIDDEN',
                        'Only data owner can perform this operation'
                    ).with_status(403)
        return inner
