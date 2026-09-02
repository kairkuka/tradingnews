from app.config.event_types import (
    EventDirectionality,
    canonical_event_type,
    get_directionality,
    resolve_event_type,
)


def test_event_type_resolution_prefers_specific_aliases() -> None:
    event = resolve_event_type("United States Core CPI YoY")

    assert event is not None
    assert event.canonical_type == "Core CPI"


def test_event_type_resolution_handles_nonfarm_alias() -> None:
    event = resolve_event_type("US Non-Farm Payrolls")

    assert event is not None
    assert event.canonical_type == "NFP"


def test_canonical_event_type_uses_country_prefix() -> None:
    assert canonical_event_type("United States", "Core CPI") == "US_CORE_CPI"


def test_directionality_uses_country_specific_override() -> None:
    assert get_directionality("US", "Unemployment Rate") == EventDirectionality.HIGHER_IS_DOVISH

