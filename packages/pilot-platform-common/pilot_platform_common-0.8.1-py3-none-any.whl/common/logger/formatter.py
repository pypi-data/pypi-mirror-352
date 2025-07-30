# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


import os
from logging import LogRecord
from typing import Any
from typing import Dict

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom formatter to format logging records as json strings."""

    def __init__(self, *args: Any, **kwds: Any) -> None:
        super().__init__(*args, **kwds)

        self.namespace = None

    def get_namespace(self) -> str:
        """Get namespace for current service."""

        if self.namespace is None:
            self.namespace = os.environ.get('namespace', 'unknown')

        return self.namespace

    def add_fields(self, log_record: Dict[str, Any], record: LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields into the log record."""

        super().add_fields(log_record, record, message_dict)

        log_record['level'] = record.levelname
        log_record['namespace'] = self.get_namespace()
        log_record['sub_name'] = record.name


def get_formatter() -> CustomJsonFormatter:
    """Return instance of default formatter."""

    return CustomJsonFormatter(fmt='%(asctime)s %(namespace)s %(sub_name)s %(level)s %(message)s')
