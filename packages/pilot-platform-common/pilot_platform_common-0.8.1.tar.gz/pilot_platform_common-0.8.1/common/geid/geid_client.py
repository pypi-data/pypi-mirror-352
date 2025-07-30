# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


from common.models.service_id_generator import GenerateId


class GEIDClient:
    def get_GEID(self) -> str:
        new_id = GenerateId()
        uniq_id = new_id.generate_id() + '-' + new_id.time_hash()
        return uniq_id

    def get_GEID_bulk(self, number: int) -> list:
        id_list = []
        for _ in range(number):
            new_id = GenerateId()
            uniq_id = new_id.generate_id() + '-' + new_id.time_hash()
            id_list.append(uniq_id)
        return id_list
