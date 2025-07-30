# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


import logging

import httpx
import jwt
from starlette.requests import Request

from common.jwt_handler.jwt_handler_exception import JWTHandlerError
from common.jwt_handler.jwt_handler_exception import JWTHandlerException

logger = logging.getLogger('pilot.common')


class JWTHandler:
    def __init__(self, public_key: str) -> None:
        self.public_key = public_key

    def _get_token_from_authorization(self, request: Request) -> str:
        token = request.headers.get('Authorization')
        if token:
            result = token.split()[1]
            logger.debug(f'Got token from authorization: {result}')
            return result

    def _get_token_from_cookies(self, request: Request) -> str:
        cookies = request.headers.get('cookie')
        if cookies:
            cookies = cookies.split(';')
            for cookie in cookies:
                cookie = cookie.strip()
                if cookie.startswith('AUTH='):
                    result = cookie[5:]
                    logger.debug(f'Got token from cookies: {result}')
                    return result

    def get_token(self, request: Request) -> str:
        token = self._get_token_from_authorization(request)
        if not token:
            token = self._get_token_from_cookies(request)
            if not token:
                logger.error(f'Failed to get token from headers: {request.headers}')
                raise JWTHandlerException(JWTHandlerError.GET_TOKEN_ERROR)
        return token

    def decode_validate_token(self, encoded_token: str) -> dict:
        try:
            expected_audience = ['minio', 'account']
            decoded_token = jwt.decode(
                jwt=encoded_token,
                key=self.public_key,
                algorithms='RS256',
                audience=expected_audience,
                options={
                    'verify_signature': True,  # cryptographic signature
                    'verify_aud': True,  # audience
                    'verify_iss': True,  # issuer
                    'verify_exp': True,  # expiration
                    'verify_iat': True,  # issued at
                    'verify_nbf': True,  # not before
                },
            )
            return decoded_token
        except Exception as e:
            logger.error(f'Failed to validate token: {e}')
            raise JWTHandlerException(JWTHandlerError.VALIDATE_TOKEN_ERROR)

    async def get_current_identity(self, auth_service: str, decoded_token: dict) -> dict:
        username: str = decoded_token.get('preferred_username')
        if not username:
            return None

        # get user data from Auth service
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{auth_service}/v1/admin/user', params={'username': username, 'exact': True})
        if response.status_code != 200:
            msg = f'Failed to get user {username} from Auth service ({response.status_code})'
            logger.error(msg)
            raise Exception(msg)
        user = response.json()['result']
        if not user or user['attributes'].get('status') != 'active':
            logger.error(f'User {username} is not active')
            return None

        return {
            'user_id': user['id'],
            'username': username,
            'role': user['role'] if 'role' in user else None,
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'realm_roles': decoded_token['realm_access']['roles']
            if ('realm_access' in decoded_token and 'roles' in decoded_token['realm_access'])
            else [],
        }
