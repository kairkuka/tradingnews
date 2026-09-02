import json
import logging

from app.logging import JsonFormatter


def test_json_formatter_outputs_required_structured_fields() -> None:
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="processed",
        args=(),
        exc_info=None,
    )
    record.service = "news-impact-bot"
    record.job = "calendar"
    record.event_id = "event-1"
    record.symbol = "XAUUSD"
    record.duration = 0.12
    record.status = "ok"
    record.records_processed = 3
    record.error = None

    payload = json.loads(JsonFormatter().format(record))

    assert payload["service"] == "news-impact-bot"
    assert payload["job"] == "calendar"
    assert payload["event_id"] == "event-1"
    assert payload["symbol"] == "XAUUSD"
    assert payload["duration"] == 0.12
    assert payload["status"] == "ok"
    assert payload["records_processed"] == 3
    assert payload["error"] is None

