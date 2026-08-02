import json
import logging
from contextvars import ContextVar
from datetime import (
    UTC,
    datetime,
)
from logging.config import dictConfig
from typing import Any

request_id_context: ContextVar[str] = ContextVar(
    "request_id",
    default="-",
)


class RequestIdFilter(logging.Filter):
    def filter(
        self,
        record: logging.LogRecord,
    ) -> bool:
        record.request_id = request_id_context.get()

        return True


class JsonFormatter(logging.Formatter):
    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        payload: dict[str, Any] = {
            "timestamp": (datetime.now(UTC).isoformat()),
            "level": record.levelname,
            "logger": record.name,
            "message": (record.getMessage()),
            "request_id": getattr(
                record,
                "request_id",
                "-",
            ),
        }

        for field_name in (
            "method",
            "path",
            "status_code",
            "duration_ms",
        ):
            field_value = getattr(
                record,
                field_name,
                None,
            )

            if field_value is not None:
                payload[field_name] = field_value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(
            payload,
            ensure_ascii=False,
        )


def configure_logging(
    log_level: str,
) -> None:
    normalized_level = log_level.upper()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": (False),
            "filters": {
                "request_id": {
                    "()": RequestIdFilter,
                }
            },
            "formatters": {
                "json": {
                    "()": JsonFormatter,
                }
            },
            "handlers": {
                "console": {
                    "class": ("logging.StreamHandler"),
                    "formatter": "json",
                    "filters": ["request_id"],
                    "stream": ("ext://sys.stdout"),
                }
            },
            "root": {
                "handlers": ["console"],
                "level": normalized_level,
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["console"],
                    "level": (normalized_level),
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console"],
                    "level": (normalized_level),
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": [],
                    "propagate": False,
                },
            },
        }
    )
