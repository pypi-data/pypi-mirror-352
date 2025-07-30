# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


from .boto3_admin_client import get_boto3_admin_client
from .boto3_client import TokenError
from .boto3_client import get_boto3_client
from .minio_policy_client import NotFoundError
from .minio_policy_client import get_minio_policy_client

__all__ = [
    'get_boto3_admin_client',
    'get_boto3_client',
    'get_minio_policy_client',
    'TokenError',
    'NotFoundError',
]
