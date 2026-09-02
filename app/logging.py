import json
import logging
from datetime import UTC, datetime
from typing import Any

STRUCTURED_FIELDS = (
    "service",
    "job",
    "event_id",
    "symbol",
    "duration",
    "status",
    "records_processed",
    "error",
)

SENSITIVE_MARKERS = ("api_key", "token", "secret", "password", "credential")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }

        for field in STRUCTURED_FIELDS:
            payload[field] = self._sanitize(field, getattr(record, field, None))

        if record.exc_info:
            payload["error"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str, separators=(",", ":"))

    @staticmethod
    def _sanitize(key: str, value: Any) -> Any:
        lowered = key.lower()
        if any(marker in lowered for marker in SENSITIVE_MARKERS) and value:
            return "[redacted]"
        return value


def configure_logging(service: str, level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.LoggerAdapter(logging.getLogger(__name__), {"service": service})

