import random
from datetime import UTC, datetime, timedelta


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(UTC)


def utc_delta(
    *,
    days: int | None = None,
    hours: int | None = None,
    minutes: int | None = None,
    seconds: int | None = None,
) -> datetime:
    """Get UTC time shifted by the specified delta.

    Use negative values to get time in the past.
    """
    params = {}
    if days:
        params["days"] = days
    if hours:
        params["hours"] = hours
    if minutes:
        params["minutes"] = minutes
    if seconds:
        params["seconds"] = seconds
    return datetime.now(UTC) + timedelta(**params)


def utc_random(
    *,
    from_time: datetime | None = None,
    range_hours: int = 0,
    range_minutes: int = 0,
    range_seconds: int = 0,
) -> datetime:
    """Generate random UTC time within specified range from base time.

    Returns random time between from_time and from_time + range_*.
    """
    if from_time is None:
        from_time = utc_now()
    to_time = from_time + timedelta(hours=range_hours, minutes=range_minutes, seconds=range_seconds)
    return from_time + (to_time - from_time) * random.random()
