# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


import time
import uuid


class GenerateId:
    def generate_id(self):
        return str(uuid.uuid4())

    def time_hash(self):
        return str(time.time())[0:10]
