import logging
import os
from logging.config import dictConfig


def configure_logging():
    """Configure application-wide logging.

    - Uses level from LOG_LEVEL (default INFO)
    - Plain text formatter by default; set LOG_FORMAT=json for JSON lines
    - Logs to stdout for container platforms (Render, etc.)
    """

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    fmt = os.getenv("LOG_FORMAT", "plain").lower()

    if fmt == "json":
        # Minimal JSON formatter without extra dependencies
        # We serialize a subset of fields to keep output compact
        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                import json
                base = {
                    "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
                    "level": record.levelname,
                    "logger": record.name,
                    "msg": record.getMessage(),
                }
                # Attach optional context if present
                for key in ("request_id", "job_id", "path", "method", "status_code", "duration_ms"):
                    if hasattr(record, key):
                        base[key] = getattr(record, key)
                if record.exc_info:
                    base["exc_info"] = self.formatException(record.exc_info)
                return json.dumps(base, ensure_ascii=False)

        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": lambda: formatter,
                }
            },
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"level": level, "handlers": ["stdout"]},
        }
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

