from datetime import datetime


def parse_date(value: str, ignore_tz: bool = False) -> datetime:
    """Parse date string in various formats, with timezone handling.

    Converts 'Z' suffix to '+00:00' for ISO format compatibility.
    Use ignore_tz=True to strip timezone info from the result.
    """
    if value.lower().endswith("z"):
        value = value[:-1] + "+00:00"
    date_formats = [
        "%Y-%m-%d %H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M%z",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d",
        # Add more formats as needed
    ]

    for fmt in date_formats:
        try:
            dt = datetime.strptime(value, fmt)  # noqa: DTZ007
            if ignore_tz and dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)
            return dt  # noqa: TRY300
        except ValueError:
            continue
    raise ValueError(f"Time data '{value}' does not match any known format.")
