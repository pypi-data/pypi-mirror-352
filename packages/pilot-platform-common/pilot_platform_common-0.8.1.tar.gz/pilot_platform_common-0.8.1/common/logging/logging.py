# Copyright (C) 2022-Present Indoc Systems
#
# Licensed under the GNU AFFERO GENERAL PUBLIC LICENSE,
# Version 3.0 (the "License") available at https://www.gnu.org/licenses/agpl-3.0.en.html.
# You may not use this file except in compliance with the License.


import datetime as dt
import json
import logging
import logging.config
from collections.abc import Mapping
from typing import Any
from typing import Union

AUDIT = logging.INFO + 5


class Logger(logging.Logger):
    def audit(self, message: str, **kwds: Any) -> None:
        ...


class JsonFormatter(logging.Formatter):
    """Convert LogRecord to json string."""

    def format(self, record: logging.LogRecord) -> str:
        asctime = dt.datetime.fromtimestamp(record.created, tz=dt.timezone.utc).isoformat()
        level = record.levelname
        logger = record.name
        message = record.getMessage()
        exc_info = None
        if record.exc_info:
            exc_info = self.formatException(record.exc_info)
        details = None
        if isinstance(record.args, Mapping):
            details = record.args

        return json.dumps(
            {
                'asctime': asctime,
                'level': level,
                'logger': logger,
                'message': message,
                'exc_info': exc_info,
                'details': details,
            }
        )


def extend_logger_class() -> None:
    """Register a new level and extend the default logging.Logger class with an additional method.

    Using setLoggerClass() is not feasible in this case, since logging.Logger instances could potentially be already
    created before the invocation of this function.
    """

    def audit(self: Logger, message: str, **kwds: Any) -> None:
        """Log message and **kwds with severity 'AUDIT'."""

        if self.isEnabledFor(AUDIT):
            args = (kwds,) if kwds else None
            self._log(AUDIT, message, args=args)

    logging.addLevelName(AUDIT, 'AUDIT')

    logger_class = logging.getLoggerClass()
    logger_class.audit = audit


def configure_logging(level: int, formatter: str = 'json', namespaces: Union[list[str], None] = None) -> None:
    """Configure python logging system using a config dictionary."""

    formatters = {
        'default': {
            'format': '%(asctime)s\t%(levelname)s\t[%(name)s]\t%(message)s',
        },
        'json': {
            '()': JsonFormatter,
        },
    }
    if formatter not in formatters:
        formatter = next(iter(formatters))

    if namespaces is None:
        namespaces = ['pilot', 'asyncio', 'uvicorn']

    config = {
        'handlers': ['stdout'],
        'level': level,
    }
    loggers = dict.fromkeys(namespaces, config)

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': formatters,
        'handlers': {
            'stdout': {
                'formatter': formatter,
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': loggers,
    }

    extend_logger_class()

    logging.config.dictConfig(logging_config)
