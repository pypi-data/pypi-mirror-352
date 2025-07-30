# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


import copy


class FileDataAttribute:
    """The class is for Altas file_data entity attirbute."""

    item_id: str
    name: str
    file_name: str
    path: str
    qualifiedName: str
    archived: bool
    container_code: str
    container_type: str

    def __init__(
        self,
        item_id: str,
        file_name: str,
        path: str,
        zone: int,
        container_code: str,
        container_type: str,
        archive: bool,
    ) -> None:

        self.item_id = item_id

        # these two are mandatory and default attribute
        self.name = item_id
        self.qualifiedName = item_id

        self.zone = zone

        self.file_name = file_name
        self.path = path
        self.container_code = container_code
        self.container_type = container_type
        self.archived = archive

    def json(self):
        return self.__dict__


class Entity:
    typeName: str
    attributes: FileDataAttribute
    # isIncomplete: bool = False
    # status: str = 'ACTIVE'
    createdBy: str = ''
    # version: int = 0
    # relationshipAttributes: dict
    # customAttributes: dict
    # labels: list

    def __init__(self, typeName: str, attributes: FileDataAttribute, createdBy: str = ''):
        self.typeName = typeName
        self.attributes = copy.deepcopy(attributes)
        self.createdBy = createdBy

    def json(self):
        res = {}
        for key, val in self.__dict__.items():
            if isinstance(val, str) or isinstance(val, int):
                res.update({key: val})
            # if we have sub class type, using the json()
            # function to format the return
            else:
                res.update({key: val.json()})

        return res
