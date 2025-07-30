# -*- coding: utf-8 -*-
from typing import List, Callable

import bottle
from pip_services4_commons.errors import UnauthorizedException

from pip_services4_http.controller.HttpResponseSender import HttpResponseSender


class RoleAuthorizer:
    def user_in_roles(self, roles: List[str]) -> Callable:
        def inner():
            user = bottle.request.environ.get('bottle.request.ext.user')
            if user is None:
                raise UnauthorizedException(
                    None,
                    'NOT_SIGNED',
                    'User must be signed in to perform this operation'
                ).with_status(401)
            else:
                authorized = False
                for role in roles:
                    authorized = authorized or role in user.get('roles', [])

                if not authorized:
                    raise UnauthorizedException(
                        None,
                        'NOT_IN_ROLE',
                        'User must be ' +
                        ' or '.join(roles) + ' to perform this operation'
                    ).with_details('roles', roles).with_status(403)

        return inner

    def user_in_role(self, role: str) -> Callable:
        return self.user_in_roles([role])

    def admin(self) -> Callable:
        return self.user_in_role('admin')
