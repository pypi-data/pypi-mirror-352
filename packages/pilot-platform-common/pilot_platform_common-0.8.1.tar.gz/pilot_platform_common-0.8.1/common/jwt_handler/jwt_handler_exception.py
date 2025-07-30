# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


from enum import Enum


class JWTHandlerError(Enum):
    GET_TOKEN_ERROR = 'Failed to get token'
    VALIDATE_TOKEN_ERROR = 'Failed to validate token'


class JWTHandlerException(Exception):
    def __init__(self, error: JWTHandlerError):
        self.error = error

    def __str__(self):
        return self.error.value
