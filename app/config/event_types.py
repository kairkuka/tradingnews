from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from re import sub
from types import MappingProxyType


class EventCategory(StrEnum):
    INFLATION = "inflation"
    EMPLOYMENT = "employment"
    GROWTH = "growth"
    BUSINESS_ACTIVITY = "business_activity"
    CONSUMER = "consumer"
    HOUSING = "housing"
    FEDERAL_RESERVE = "federal_reserve"


class EventDirectionality(StrEnum):
    HIGHER_IS_HAWKISH = "HIGHER_IS_HAWKISH"
    HIGHER_IS_DOVISH = "HIGHER_IS_DOVISH"
    NEUTRAL = "NEUTRAL"


@dataclass(frozen=True)
class EconomicEventTypeConfig:
    canonical_type: str
    category: EventCategory
    directionality: EventDirectionality
    aliases: tuple[str, ...]


SUPPORTED_EVENT_TYPES: Mapping[str, EconomicEventTypeConfig] = MappingProxyType(
    {
        "CPI": EconomicEventTypeConfig(
            "CPI",
            EventCategory.INFLATION,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("CPI", "Consumer Price Index"),
        ),
        "Core CPI": EconomicEventTypeConfig(
            "Core CPI",
            EventCategory.INFLATION,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Core CPI", "Core Consumer Price Index"),
        ),
        "PCE": EconomicEventTypeConfig(
            "PCE",
            EventCategory.INFLATION,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("PCE", "Personal Consumption Expenditures"),
        ),
        "Core PCE": EconomicEventTypeConfig(
            "Core PCE",
            EventCategory.INFLATION,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Core PCE", "Core Personal Consumption Expenditures"),
        ),
        "PPI": EconomicEventTypeConfig(
            "PPI",
            EventCategory.INFLATION,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("PPI", "Producer Price Index"),
        ),
        "Core PPI": EconomicEventTypeConfig(
            "Core PPI",
            EventCategory.INFLATION,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Core PPI", "Core Producer Price Index"),
        ),
        "NFP": EconomicEventTypeConfig(
            "NFP",
            EventCategory.EMPLOYMENT,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("NFP", "Non-Farm Payrolls", "Nonfarm Payrolls"),
        ),
        "Unemployment Rate": EconomicEventTypeConfig(
            "Unemployment Rate",
            EventCategory.EMPLOYMENT,
            EventDirectionality.HIGHER_IS_DOVISH,
            ("Unemployment Rate", "Unemployment"),
        ),
        "Average Hourly Earnings": EconomicEventTypeConfig(
            "Average Hourly Earnings",
            EventCategory.EMPLOYMENT,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Average Hourly Earnings", "AHE"),
        ),
        "Initial Jobless Claims": EconomicEventTypeConfig(
            "Initial Jobless Claims",
            EventCategory.EMPLOYMENT,
            EventDirectionality.HIGHER_IS_DOVISH,
            ("Initial Jobless Claims",),
        ),
        "Continuing Claims": EconomicEventTypeConfig(
            "Continuing Claims",
            EventCategory.EMPLOYMENT,
            EventDirectionality.HIGHER_IS_DOVISH,
            ("Continuing Claims",),
        ),
        "JOLTS": EconomicEventTypeConfig(
            "JOLTS",
            EventCategory.EMPLOYMENT,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("JOLTS", "JOLTS Job Openings"),
        ),
        "ADP Employment": EconomicEventTypeConfig(
            "ADP Employment",
            EventCategory.EMPLOYMENT,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("ADP Employment", "ADP Nonfarm Employment Change"),
        ),
        "GDP": EconomicEventTypeConfig(
            "GDP",
            EventCategory.GROWTH,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("GDP", "Gross Domestic Product"),
        ),
        "Retail Sales": EconomicEventTypeConfig(
            "Retail Sales",
            EventCategory.GROWTH,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Retail Sales",),
        ),
        "Industrial Production": EconomicEventTypeConfig(
            "Industrial Production",
            EventCategory.GROWTH,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Industrial Production",),
        ),
        "Durable Goods": EconomicEventTypeConfig(
            "Durable Goods",
            EventCategory.GROWTH,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Durable Goods", "Durable Goods Orders"),
        ),
        "ISM Manufacturing": EconomicEventTypeConfig(
            "ISM Manufacturing",
            EventCategory.BUSINESS_ACTIVITY,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("ISM Manufacturing", "ISM Manufacturing PMI"),
        ),
        "ISM Services": EconomicEventTypeConfig(
            "ISM Services",
            EventCategory.BUSINESS_ACTIVITY,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("ISM Services", "ISM Services PMI"),
        ),
        "Manufacturing PMI": EconomicEventTypeConfig(
            "Manufacturing PMI",
            EventCategory.BUSINESS_ACTIVITY,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Manufacturing PMI",),
        ),
        "Services PMI": EconomicEventTypeConfig(
            "Services PMI",
            EventCategory.BUSINESS_ACTIVITY,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Services PMI",),
        ),
        "Composite PMI": EconomicEventTypeConfig(
            "Composite PMI",
            EventCategory.BUSINESS_ACTIVITY,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Composite PMI",),
        ),
        "Consumer Confidence": EconomicEventTypeConfig(
            "Consumer Confidence",
            EventCategory.CONSUMER,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Consumer Confidence",),
        ),
        "Michigan Consumer Sentiment": EconomicEventTypeConfig(
            "Michigan Consumer Sentiment",
            EventCategory.CONSUMER,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Michigan Consumer Sentiment", "University of Michigan Consumer Sentiment"),
        ),
        "Housing Starts": EconomicEventTypeConfig(
            "Housing Starts",
            EventCategory.HOUSING,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Housing Starts",),
        ),
        "Building Permits": EconomicEventTypeConfig(
            "Building Permits",
            EventCategory.HOUSING,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Building Permits",),
        ),
        "Existing Home Sales": EconomicEventTypeConfig(
            "Existing Home Sales",
            EventCategory.HOUSING,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("Existing Home Sales",),
        ),
        "New Home Sales": EconomicEventTypeConfig(
            "New Home Sales",
            EventCategory.HOUSING,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("New Home Sales",),
        ),
        "FOMC Rate Decision": EconomicEventTypeConfig(
            "FOMC Rate Decision",
            EventCategory.FEDERAL_RESERVE,
            EventDirectionality.HIGHER_IS_HAWKISH,
            ("FOMC Rate Decision", "Fed Interest Rate Decision", "Federal Funds Rate"),
        ),
        "FOMC Statement": EconomicEventTypeConfig(
            "FOMC Statement",
            EventCategory.FEDERAL_RESERVE,
            EventDirectionality.NEUTRAL,
            ("FOMC Statement",),
        ),
        "FOMC Minutes": EconomicEventTypeConfig(
            "FOMC Minutes",
            EventCategory.FEDERAL_RESERVE,
            EventDirectionality.NEUTRAL,
            ("FOMC Minutes",),
        ),
        "Powell Press Conference": EconomicEventTypeConfig(
            "Powell Press Conference",
            EventCategory.FEDERAL_RESERVE,
            EventDirectionality.NEUTRAL,
            ("Powell Press Conference", "Fed Chair Powell Press Conference"),
        ),
        "Fed Speaker": EconomicEventTypeConfig(
            "Fed Speaker",
            EventCategory.FEDERAL_RESERVE,
            EventDirectionality.NEUTRAL,
            ("Fed Speaker", "FOMC Member Speaks", "Fed Chair Speech"),
        ),
    }
)

EVENT_DIRECTIONALITY: Mapping[str, EventDirectionality] = MappingProxyType(
    {
        "US_CPI": EventDirectionality.HIGHER_IS_HAWKISH,
        "US_CORE_CPI": EventDirectionality.HIGHER_IS_HAWKISH,
        "US_UNEMPLOYMENT_RATE": EventDirectionality.HIGHER_IS_DOVISH,
        "US_NFP": EventDirectionality.HIGHER_IS_HAWKISH,
    }
)

_COUNTRY_ALIASES: Mapping[str, str] = MappingProxyType(
    {
        "UNITED STATES": "US",
        "USA": "US",
        "U S": "US",
        "U S A": "US",
    }
)


def _normalize_label(value: str) -> str:
    normalized = value.upper().replace("&", " AND ")
    normalized = sub(r"[^A-Z0-9]+", " ", normalized)
    return " ".join(normalized.split())


_ALIAS_TO_EVENT: Mapping[str, EconomicEventTypeConfig] = MappingProxyType(
    {
        _normalize_label(alias): event
        for event in SUPPORTED_EVENT_TYPES.values()
        for alias in (event.canonical_type, *event.aliases)
    }
)


def normalize_country(country: str) -> str:
    normalized = _normalize_label(country)
    return _COUNTRY_ALIASES.get(normalized, normalized.replace(" ", "_"))


def event_type_slug(event_type: str) -> str:
    return _normalize_label(event_type).replace(" ", "_")


def canonical_event_type(country: str, event_type: str) -> str:
    return f"{normalize_country(country)}_{event_type_slug(event_type)}"


def resolve_event_type(label: str) -> EconomicEventTypeConfig | None:
    normalized = _normalize_label(label)
    exact = _ALIAS_TO_EVENT.get(normalized)
    if exact is not None:
        return exact

    aliases_by_length = sorted(
        _ALIAS_TO_EVENT.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    for alias, event in aliases_by_length:
        if f" {alias} " in f" {normalized} ":
            return event
    return None


def get_directionality(country: str, event_type: str) -> EventDirectionality:
    canonical = canonical_event_type(country, event_type)
    mapped = EVENT_DIRECTIONALITY.get(canonical)
    if mapped is not None:
        return mapped

    event = SUPPORTED_EVENT_TYPES[event_type]
    return event.directionality
