# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


from enum import Enum


class VaultClientError(Enum):
    CONNECT_ERROR = 'Failed to connect to Vault'
    RESPONSE_ERROR = 'Received invalid response from Vault'


class VaultClientException(Exception):
    def __init__(self, error: VaultClientError):
        self.error = error

    def __str__(self):
        return self.error.value
