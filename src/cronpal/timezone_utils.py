"""Timezone utilities for cron expressions."""

from datetime import datetime
from typing import List, Optional, Union

import pytz


def get_timezone(tz_name: Optional[str] = None) -> pytz.tzinfo.BaseTzInfo:
    """
    Get a timezone object from a timezone name.

    Args:
        tz_name: The timezone name (e.g., 'US/Eastern', 'Europe/London').
                 If None, returns the system's local timezone.

    Returns:
        A timezone object.

    Raises:
        ValueError: If the timezone name is invalid.
    """
    if tz_name is None:
        # Try to get system timezone
        try:
            import tzlocal
            return tzlocal.get_localzone()
        except (ImportError, Exception):
            # Fall back to UTC if we can't determine local timezone
            return pytz.UTC

    try:
        return pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        raise ValueError(f"Unknown timezone: '{tz_name}'")


def convert_to_timezone(dt: datetime, tz: Union[str, pytz.tzinfo.BaseTzInfo]) -> datetime:
    """
    Convert a datetime to a specific timezone.

    Args:
        dt: The datetime to convert (can be naive or aware).
        tz: The target timezone (string name or timezone object).

    Returns:
        A timezone-aware datetime in the target timezone.
    """
    if isinstance(tz, str):
        tz = get_timezone(tz)

    # If datetime is naive, assume it's in the target timezone
    if dt.tzinfo is None:
        return tz.localize(dt)

    # If datetime is already aware, convert it
    return dt.astimezone(tz)


def localize_datetime(dt: datetime, tz: Union[str, pytz.tzinfo.BaseTzInfo]) -> datetime:
    """
    Localize a naive datetime to a specific timezone.

    Args:
        dt: A naive datetime object.
        tz: The timezone to localize to (string name or timezone object).

    Returns:
        A timezone-aware datetime.

    Raises:
        ValueError: If the datetime is already timezone-aware.
    """
    if dt.tzinfo is not None:
        raise ValueError("Datetime is already timezone-aware")

    if isinstance(tz, str):
        tz = get_timezone(tz)

    return tz.localize(dt)


def get_current_time(tz: Optional[Union[str, pytz.tzinfo.BaseTzInfo]] = None) -> datetime:
    """
    Get the current time in a specific timezone.

    Args:
        tz: The timezone (string name or timezone object).
            If None, returns current time in local timezone.

    Returns:
        Current timezone-aware datetime.
    """
    if tz is None:
        tz = get_timezone(None)
    elif isinstance(tz, str):
        tz = get_timezone(tz)

    return datetime.now(tz)


def list_common_timezones() -> List[str]:
    """
    Get a list of common timezone names.

    Returns:
        List of common timezone names.
    """
    return pytz.common_timezones


def is_valid_timezone(tz_name: str) -> bool:
    """
    Check if a timezone name is valid.

    Args:
        tz_name: The timezone name to check.

    Returns:
        True if the timezone name is valid, False otherwise.
    """
    return tz_name in pytz.all_timezones


def get_timezone_offset(tz: Union[str, pytz.tzinfo.BaseTzInfo], dt: Optional[datetime] = None) -> str:
    """
    Get the UTC offset for a timezone at a specific time.

    Args:
        tz: The timezone (string name or timezone object).
        dt: The datetime to get the offset for.
            If None, uses current time.

    Returns:
        UTC offset as a string (e.g., '+05:30', '-08:00').
    """
    if isinstance(tz, str):
        tz = get_timezone(tz)

    if dt is None:
        dt = datetime.now()

    # Localize the datetime to the timezone
    if dt.tzinfo is None:
        dt = tz.localize(dt)
    else:
        dt = dt.astimezone(tz)

    # Get the UTC offset
    offset = dt.strftime('%z')

    # Format as +HH:MM or -HH:MM
    if offset:
        return f"{offset[:3]}:{offset[3:]}"
    return "+00:00"


def get_timezone_abbreviation(tz: Union[str, pytz.tzinfo.BaseTzInfo], dt: Optional[datetime] = None) -> str:
    """
    Get the timezone abbreviation (e.g., 'EST', 'PDT').

    Args:
        tz: The timezone (string name or timezone object).
        dt: The datetime to get the abbreviation for.
            If None, uses current time.

    Returns:
        Timezone abbreviation.
    """
    if isinstance(tz, str):
        tz = get_timezone(tz)

    if dt is None:
        dt = datetime.now()

    # Localize the datetime to the timezone
    if dt.tzinfo is None:
        dt = tz.localize(dt)
    else:
        dt = dt.astimezone(tz)

    return dt.strftime('%Z')


def format_datetime_with_timezone(dt: datetime, tz: Optional[Union[str, pytz.tzinfo.BaseTzInfo]] = None) -> str:
    """
    Format a datetime with timezone information.

    Args:
        dt: The datetime to format.
        tz: The timezone to convert to before formatting.
            If None and dt is naive, uses local timezone.

    Returns:
        Formatted datetime string with timezone.
    """
    # Convert to target timezone if specified
    if tz is not None:
        dt = convert_to_timezone(dt, tz)
    elif dt.tzinfo is None:
        # If naive and no timezone specified, use local
        dt = convert_to_timezone(dt, get_timezone(None))

    # Format with timezone abbreviation and offset
    tz_abbrev = dt.strftime('%Z')
    tz_offset = dt.strftime('%z')
    if tz_offset:
        tz_offset = f"{tz_offset[:3]}:{tz_offset[3:]}"

    return dt.strftime(f"%Y-%m-%d %H:%M:%S %A {tz_abbrev} ({tz_offset})")


def convert_between_timezones(dt: datetime, from_tz: Union[str, pytz.tzinfo.BaseTzInfo],
                              to_tz: Union[str, pytz.tzinfo.BaseTzInfo]) -> datetime:
    """
    Convert a datetime from one timezone to another.

    Args:
        dt: The datetime to convert (should be naive).
        from_tz: The source timezone.
        to_tz: The target timezone.

    Returns:
        Datetime in the target timezone.
    """
    if isinstance(from_tz, str):
        from_tz = get_timezone(from_tz)
    if isinstance(to_tz, str):
        to_tz = get_timezone(to_tz)

    # If datetime is naive, localize it to source timezone
    if dt.tzinfo is None:
        dt = from_tz.localize(dt)
    # If it's already aware but not in from_tz, convert to from_tz first
    elif dt.tzinfo != from_tz:
        dt = dt.astimezone(from_tz)

    # Convert to target timezone
    return dt.astimezone(to_tz)