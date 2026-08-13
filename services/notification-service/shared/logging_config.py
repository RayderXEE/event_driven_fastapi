"""
Structured JSON logging configuration for all microservices.

Uses python-json-logger for production-ready JSON log output.
Falls back to standard formatting when LOG_FORMAT != json.
"""

import logging
import os
import sys
from typing import Optional

try:
    from pythonjsonlogger import jsonlogger
    HAS_JSON_LOGGER = True
except ImportError:
    HAS_JSON_LOGGER = False


def setup_logging(
    level: str = "INFO",
    log_format: str = "json",
    service_name: str = "service",
) -> logging.Logger:
    """
    Configure and return the root logger.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: "json" for structured JSON logs, "text" for human-readable
        service_name: Service name included in every log record

    Returns:
        Configured root logger
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    if log_format == "json" and HAS_JSON_LOGGER:
        formatter = jsonlogger.JsonFormatter(
            fmt=(
                "%(asctime)s %(levelname)s %(name)s %(message)s "
                "service=%(service_name)s"
            ),
            datefmt="%Y-%m-%dT%H:%M:%S%z",
            rename_fields={
                "levelname": "level",
                "name": "logger",
            },
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Add service_name as a filter
    class ServiceNameFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            record.service_name = service_name  # type: ignore[attr-defined]
            return True

    root_logger.addFilter(ServiceNameFilter())

    # Suppress noisy loggers
    logging.getLogger("aiokafka").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    return logging.getLogger(service_name)


class LogContext:
    """
    Context manager that adds extra fields to log records.

    Usage:
        async with LogContext(logger, order_id=42, action="create"):
            logger.info("Processing order")
            # -> {"order_id": 42, "action": "create", ...}
    """

    def __init__(self, logger: logging.Logger, **extra: dict):
        self.logger = logger
        self.extra = extra
        self.old_factory = logging.getLogRecordFactory()

    def __enter__(self):
        old_factory = logging.getLogRecordFactory()

        def factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            for key, value in self.extra.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(factory)
        return self.logger

    def __exit__(self, *args):
        logging.setLogRecordFactory(self.old_factory)
