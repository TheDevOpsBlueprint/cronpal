"""Time calculation utilities for cron expressions."""

import calendar
from datetime import datetime, timedelta
from typing import Optional, Tuple


def get_next_minute(dt: datetime) -> datetime:
    """
    Get the next minute from the given datetime.

    Args:
        dt: The datetime to increment.

    Returns:
        A datetime object representing the next minute.
    """
    return dt + timedelta(minutes=1)


def get_previous_minute(dt: datetime) -> datetime:
    """
    Get the previous minute from the given datetime.

    Args:
        dt: The datetime to decrement.

    Returns:
        A datetime object representing the previous minute.
    """
    return dt - timedelta(minutes=1)


def get_next_hour(dt: datetime) -> datetime:
    """
    Get the next hour from the given datetime (minute set to 0).

    Args:
        dt: The datetime to increment.

    Returns:
        A datetime object at the start of the next hour.
    """
    next_hour = dt.replace(minute=0, second=0, microsecond=0)
    return next_hour + timedelta(hours=1)


def get_previous_hour(dt: datetime) -> datetime:
    """
    Get the previous hour from the given datetime (minute set to 59).

    Args:
        dt: The datetime to decrement.

    Returns:
        A datetime object at the end of the previous hour.
    """
    prev_hour = dt.replace(minute=59, second=0, microsecond=0)
    return prev_hour - timedelta(hours=1)


def get_next_day(dt: datetime) -> datetime:
    """
    Get the next day from the given datetime (time set to 00:00).

    Args:
        dt: The datetime to increment.

    Returns:
        A datetime object at the start of the next day.
    """
    next_day = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return next_day + timedelta(days=1)


def get_previous_day(dt: datetime) -> datetime:
    """
    Get the previous day from the given datetime (time set to 23:59).

    Args:
        dt: The datetime to decrement.

    Returns:
        A datetime object at the end of the previous day.
    """
    prev_day = dt.replace(hour=23, minute=59, second=0, microsecond=0)
    return prev_day - timedelta(days=1)


def get_next_month(dt: datetime) -> datetime:
    """
    Get the first day of the next month.

    Args:
        dt: The datetime to increment.

    Returns:
        A datetime object at the start of the next month.
    """
    # Calculate next month
    year = dt.year
    month = dt.month + 1

    if month > 12:
        month = 1
        year += 1

    return datetime(year, month, 1, 0, 0, 0, 0)


def get_previous_month(dt: datetime) -> datetime:
    """
    Get the last day of the previous month.

    Args:
        dt: The datetime to decrement.

    Returns:
        A datetime object at the end of the previous month.
    """
    # Calculate previous month
    year = dt.year
    month = dt.month - 1

    if month < 1:
        month = 12
        year -= 1

    # Get last day of previous month
    last_day = get_days_in_month(year, month)
    return datetime(year, month, last_day, 23, 59, 0, 0)


def get_next_year(dt: datetime) -> datetime:
    """
    Get the first day of the next year.

    Args:
        dt: The datetime to increment.

    Returns:
        A datetime object at the start of the next year.
    """
    return datetime(dt.year + 1, 1, 1, 0, 0, 0, 0)


def get_previous_year(dt: datetime) -> datetime:
    """
    Get the last day of the previous year.

    Args:
        dt: The datetime to decrement.

    Returns:
        A datetime object at the end of the previous year.
    """
    return datetime(dt.year - 1, 12, 31, 23, 59, 0, 0)


def get_days_in_month(year: int, month: int) -> int:
    """
    Get the number of days in a given month.

    Args:
        year: The year.
        month: The month (1-12).

    Returns:
        The number of days in the month.
    """
    return calendar.monthrange(year, month)[1]


def is_leap_year(year: int) -> bool:
    """
    Check if a year is a leap year.

    Args:
        year: The year to check.

    Returns:
        True if it's a leap year, False otherwise.
    """
    return calendar.isleap(year)


def get_weekday(dt: datetime) -> int:
    """
    Get the weekday for a datetime (0=Monday, 6=Sunday).
    Converts to cron format (0=Sunday, 6=Saturday).

    Args:
        dt: The datetime to check.

    Returns:
        The weekday in cron format (0=Sunday, 6=Saturday).
    """
    # Python's weekday: 0=Monday, 6=Sunday
    # Cron's weekday: 0=Sunday, 6=Saturday
    python_weekday = dt.weekday()

    if python_weekday == 6:  # Sunday in Python
        return 0  # Sunday in cron
    else:
        return python_weekday + 1  # Shift Monday-Saturday


def get_month_day_count(dt: datetime) -> int:
    """
    Get the number of days in the current month of the datetime.

    Args:
        dt: The datetime to check.

    Returns:
        The number of days in the month.
    """
    return get_days_in_month(dt.year, dt.month)


def normalize_datetime(dt: datetime) -> datetime:
    """
    Normalize a datetime to remove seconds and microseconds.

    Args:
        dt: The datetime to normalize.

    Returns:
        A datetime with seconds and microseconds set to 0.
    """
    return dt.replace(second=0, microsecond=0)


def round_to_next_minute(dt: datetime) -> datetime:
    """
    Round a datetime up to the next minute if it has seconds/microseconds.

    Args:
        dt: The datetime to round.

    Returns:
        A datetime rounded up to the next minute.
    """
    if dt.second > 0 or dt.microsecond > 0:
        return normalize_datetime(dt) + timedelta(minutes=1)
    return dt


def round_to_previous_minute(dt: datetime) -> datetime:
    """
    Round a datetime down to the previous minute, removing seconds/microseconds.

    Args:
        dt: The datetime to round.

    Returns:
        A datetime rounded down to the minute.
    """
    return dt.replace(second=0, microsecond=0)


def is_valid_day_in_month(year: int, month: int, day: int) -> bool:
    """
    Check if a day is valid for a given month and year.

    Args:
        year: The year.
        month: The month (1-12).
        day: The day to check.

    Returns:
        True if the day is valid for the month, False otherwise.
    """
    if month < 1 or month > 12:
        return False
    if day < 1:
        return False

    max_day = get_days_in_month(year, month)
    return day <= max_day


def increment_month(year: int, month: int) -> Tuple[int, int]:
    """
    Increment month by 1, handling year rollover.

    Args:
        year: The current year.
        month: The current month (1-12).

    Returns:
        A tuple of (new_year, new_month).
    """
    month += 1
    if month > 12:
        month = 1
        year += 1
    return year, month


def decrement_month(year: int, month: int) -> Tuple[int, int]:
    """
    Decrement month by 1, handling year rollover.

    Args:
        year: The current year.
        month: The current month (1-12).

    Returns:
        A tuple of (new_year, new_month).
    """
    month -= 1
    if month < 1:
        month = 12
        year -= 1
    return year, month


def get_month_bounds(dt: datetime) -> Tuple[datetime, datetime]:
    """
    Get the first and last moments of the month for a datetime.

    Args:
        dt: The datetime to check.

    Returns:
        A tuple of (first_moment, last_moment) of the month.
    """
    first_day = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Get last day of month
    last_day_num = get_days_in_month(dt.year, dt.month)
    last_day = dt.replace(
        day=last_day_num,
        hour=23,
        minute=59,
        second=59,
        microsecond=999999
    )

    return first_day, last_day


def get_week_bounds(dt: datetime) -> Tuple[datetime, datetime]:
    """
    Get the first and last moments of the week for a datetime.
    Week starts on Sunday in cron.

    Args:
        dt: The datetime to check.

    Returns:
        A tuple of (first_moment, last_moment) of the week.
    """
    # Get current weekday in cron format
    cron_weekday = get_weekday(dt)

    # Calculate days to Sunday (start of week)
    days_to_sunday = cron_weekday

    # Get Sunday at 00:00
    sunday = dt - timedelta(days=days_to_sunday)
    sunday = sunday.replace(hour=0, minute=0, second=0, microsecond=0)

    # Get Saturday at 23:59:59.999999
    saturday = sunday + timedelta(days=6)
    saturday = saturday.replace(hour=23, minute=59, second=59, microsecond=999999)

    return sunday, saturday