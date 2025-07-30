# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


class ProjectException(Exception):
    status_code = 500
    error_msg = ''

    def __init__(self, status_code=None, error_msg=None):
        if status_code:
            self.status_code = status_code
        if error_msg:
            self.error_msg = error_msg
        self.content = {
            'code': self.status_code,
            'error_msg': self.error_msg,
            'result': '',
        }

    def __str__(self):
        return self.error_msg


class ProjectNotFoundException(ProjectException):
    status_code = 404
    error_msg = 'Project not found'
