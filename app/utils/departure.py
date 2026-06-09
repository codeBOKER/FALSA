from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Any, Literal
from zoneinfo import ZoneInfo

APP_TIMEZONE = "Asia/Aden"
DEPARTURE_BUCKETS = ("morning", "noon", "night")
DepartureBucket = Literal["morning", "noon", "night"]


@dataclass(frozen=True)
class DepartureRequest:
    departure_date: date | None = None
    departure_time: DepartureBucket | None = None


def now_in_aden() -> datetime:
    return datetime.now(tz=ZoneInfo(APP_TIMEZONE))


def normalize_departure_bucket(value: Any) -> DepartureBucket | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in DEPARTURE_BUCKETS:
        return text  # type: ignore[return-value]

    parsed = _parse_datetime(text)
    if parsed:
        return bucket_for_time(parsed.astimezone(ZoneInfo(APP_TIMEZONE)).time())

    parsed_time = _parse_time(text)
    if parsed_time:
        return bucket_for_time(parsed_time)

    if "morning" in text or "صباح" in text:
        return "morning"
    if "noon" in text or "afternoon" in text or "ظهر" in text:
        return "noon"
    if "night" in text or "evening" in text or "ليل" in text or "مساء" in text:
        return "night"
    return None


def bucket_for_time(value: time) -> DepartureBucket:
    if value.hour < 12:
        return "morning"
    if value.hour < 18:
        return "noon"
    return "night"


def parse_departure_request(
    *,
    travel_date: Any = None,
    travel_time: Any = None,
    travel_datetime: Any = None,
) -> DepartureRequest:
    requested_date = _parse_date_value(travel_date)
    requested_time = normalize_departure_bucket(travel_time)

    if travel_datetime:
        parsed_datetime = _parse_datetime(str(travel_datetime).strip())
        if parsed_datetime:
            aden_datetime = parsed_datetime.astimezone(ZoneInfo(APP_TIMEZONE))
            requested_date = requested_date or aden_datetime.date()
            requested_time = requested_time or bucket_for_time(aden_datetime.time())
        else:
            requested_date = requested_date or _parse_date_value(travel_datetime)
            requested_time = requested_time or normalize_departure_bucket(travel_datetime)

    return DepartureRequest(departure_date=requested_date, departure_time=requested_time)


def parse_requested_clock_time(
    *,
    travel_time: Any = None,
    travel_datetime: Any = None,
    exact_time: Any = None,
) -> time | None:
    for value in (exact_time, travel_datetime, travel_time):
        if not value:
            continue
        text = str(value).strip()
        parsed_datetime = _parse_datetime(text)
        if parsed_datetime:
            return parsed_datetime.astimezone(ZoneInfo(APP_TIMEZONE)).time().replace(
                second=0,
                microsecond=0,
            )
        parsed_time = _parse_time(text)
        if parsed_time:
            return parsed_time
    return None


def not_departed_bucket_filter(now: datetime | None = None) -> tuple[date, tuple[str, ...]]:
    aden_now = (now or now_in_aden()).astimezone(ZoneInfo(APP_TIMEZONE))
    if aden_now.time() < time(12, 0):
        return aden_now.date(), DEPARTURE_BUCKETS
    if aden_now.time() < time(18, 0):
        return aden_now.date(), ("noon", "night")
    return aden_now.date(), ("night",)


def trip_departure_date(trip: dict[str, Any]) -> date | None:
    parsed = _parse_date_value(trip.get("departure_date"))
    if parsed:
        return parsed
    parsed_datetime = _parse_datetime(str(trip.get("departure_time") or "").strip())
    if parsed_datetime:
        return parsed_datetime.astimezone(ZoneInfo(APP_TIMEZONE)).date()
    return None


def trip_departure_bucket(trip: dict[str, Any]) -> DepartureBucket | None:
    return normalize_departure_bucket(trip.get("departure_time"))


def trip_satisfies_departure_request(
    trip: dict[str, Any],
    request: DepartureRequest,
    *,
    now: datetime | None = None,
) -> bool:
    trip_date = trip_departure_date(trip)
    trip_bucket = trip_departure_bucket(trip)
    if trip_date is None or trip_bucket is None:
        return False

    today, remaining_buckets = not_departed_bucket_filter(now)
    if request.departure_date:
        if trip_date != request.departure_date:
            return False
        if request.departure_time:
            return trip_bucket == request.departure_time
        if trip_date == today:
            return trip_bucket in remaining_buckets
        return trip_date > today

    if request.departure_time and trip_bucket != request.departure_time:
        return False
    return trip_date > today or (trip_date == today and trip_bucket in remaining_buckets)


def _parse_date_value(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.astimezone(ZoneInfo(APP_TIMEZONE)).date()
    text = str(value).strip()
    if not text:
        return None
    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def _parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=ZoneInfo(APP_TIMEZONE))
    return parsed


def _parse_time(value: str) -> time | None:
    match = re.search(r"\b([01]?\d|2[0-3])(?::([0-5]\d))?\s*(am|pm)?\b", value, re.I)
    if not match:
        return None
    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    meridiem = (match.group(3) or "").lower()
    if meridiem == "pm" and hour < 12:
        hour += 12
    if meridiem == "am" and hour == 12:
        hour = 0
    return time(hour, minute)
