# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


import logging

from httpx import AsyncClient

logger = logging.getLogger('pilot.common')


async def has_permission(
    auth_url: str, project_code: str, resource: str, zone: str, operation: str, current_identity: str
):
    if current_identity['role'] == 'admin':
        role = 'platform_admin'
    else:
        if not project_code:
            logger.info('No project code and not a platform admin, permission denied')
            return False
        role = await get_project_role(project_code, current_identity)
        if not role:
            logger.info('Unable to get project role in permissions check, user might not belong to project')
            return False

    try:
        payload = {
            'role': role,
            'resource': resource,
            'zone': zone,
            'operation': operation,
            'project_code': project_code,
        }
        async with AsyncClient(timeout=15) as client:
            response = await client.get(auth_url + 'authorize', params=payload)
        if response.status_code != 200:
            error_msg = f'Error calling authorize API - {response.json()}'
            logger.info(error_msg)
            raise Exception(error_msg)
        if response.json()['result'].get('has_permission'):
            return True
        return False
    except Exception as e:
        error_msg = str(e)
        logger.info(f'Exception on authorize call: {error_msg}')
        raise Exception(f'Error calling authorize API - {error_msg}')


async def get_project_role(project_code, current_identity):
    role = None
    if current_identity['role'] == 'admin':
        role = 'platform_admin'
    else:
        for realm_role in current_identity['realm_roles']:
            # if this is a role for the correct project
            if realm_role.startswith(project_code + '-'):
                role = realm_role.replace(project_code + '-', '')
    return role


async def has_file_permission(auth_url, file_entity: dict, operation: str, current_identity: dict) -> bool:
    if file_entity['container_type'] != 'project':
        logger.info('Unsupport container type, permission denied')
        return False
    project_code = file_entity['container_code']
    username = current_identity['username']

    zone = 'greenroom' if file_entity['zone'] == 0 else 'core'

    if file_entity.get('type') == 'name_folder':
        path_for_permissions = 'name'
    elif file_entity.get('status') == 'ARCHIVED':
        path_for_permissions = 'restore_path'
    else:
        path_for_permissions = 'parent_path'
    root_folder = file_entity[path_for_permissions].split('/')[0]

    # If the user has file_any permission return True, if the file is in the users namefolder and the user has file own
    # permissions return True else False
    if not await has_permission(auth_url, project_code, 'file_any', zone, operation, current_identity):
        if root_folder != username:
            return False
        if not await has_permission(
            auth_url, project_code, 'file_in_own_namefolder', zone, operation, current_identity
        ):
            return False
    return True
