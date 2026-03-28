"""Centralized structured logging setup for the application."""

from __future__ import annotations

import logging
import sys

import structlog


def _add_cloud_logging_fields(_, __, event_dict: dict) -> dict:
    """
    Add fields expected by Google Cloud Logging so logs show up with correct severity.
    Cloud Run / GCP only map severity and message from JSON when present.
    """
    level = event_dict.get("level", "info")
    event_dict["severity"] = str(level).upper()
    if "message" not in event_dict:
        event_dict["message"] = event_dict.get("event", "")
    return event_dict


def configure_logging(log_level: str = "INFO", *, json_logs: bool = True) -> None:
    """Configure stdlib logging + structlog for consistent structured logs."""
    level = log_level.upper()
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    if json_logs:
        shared_processors.append(_add_cloud_logging_fields)

    shared_processors += [
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    stream = sys.stdout
    try:
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(line_buffering=True)
    except (OSError, AttributeError):
        pass

    logging.basicConfig(
        level=level,
        format="%(message)s",
        stream=stream,
        force=True,
    )

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    renderer = (
        structlog.processors.JSONRenderer()
        if json_logs
        else structlog.dev.ConsoleRenderer(colors=True)
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    root = logging.getLogger()
    for handler in root.handlers:
        handler.setFormatter(formatter)

    # Tame noisy third-party loggers but let uvicorn access logs through
    for name in ("httpcore", "httpx", "hpack", "markdown_it"):
        logging.getLogger(name).setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger bound to module name."""
    return structlog.get_logger(name)


def bind_log_context(**values: object) -> None:
    """Bind request-scoped values into log context."""
    structlog.contextvars.bind_contextvars(**values)


def clear_log_context() -> None:
    """Clear request-scoped log context."""
    structlog.contextvars.clear_contextvars()
