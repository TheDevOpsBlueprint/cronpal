"""Tests for time calculation utilities."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.time_utils import (
    decrement_month,
    get_days_in_month,
    get_month_bounds,
    get_month_day_count,
    get_next_day,
    get_next_hour,
    get_next_minute,
    get_next_month,
    get_next_year,
    get_week_bounds,
    get_weekday,
    increment_month,
    is_leap_year,
    is_valid_day_in_month,
    normalize_datetime,
    round_to_next_minute,
)


class TestTimeIncrements:
    """Tests for time increment functions."""

    def test_get_next_minute(self):
        """Test getting next minute."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        next_dt = get_next_minute(dt)
        assert next_dt == datetime(2024, 1, 15, 10, 31, 45)

    def test_get_next_minute_hour_rollover(self):
        """Test getting next minute with hour rollover."""
        dt = datetime(2024, 1, 15, 10, 59, 0)
        next_dt = get_next_minute(dt)
        assert next_dt == datetime(2024, 1, 15, 11, 0, 0)

    def test_get_next_minute_day_rollover(self):
        """Test getting next minute with day rollover."""
        dt = datetime(2024, 1, 15, 23, 59, 0)
        next_dt = get_next_minute(dt)
        assert next_dt == datetime(2024, 1, 16, 0, 0, 0)

    def test_get_next_hour(self):
        """Test getting next hour."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        next_dt = get_next_hour(dt)
        assert next_dt == datetime(2024, 1, 15, 11, 0, 0)

    def test_get_next_hour_day_rollover(self):
        """Test getting next hour with day rollover."""
        dt = datetime(2024, 1, 15, 23, 30, 0)
        next_dt = get_next_hour(dt)
        assert next_dt == datetime(2024, 1, 16, 0, 0, 0)

    def test_get_next_day(self):
        """Test getting next day."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        next_dt = get_next_day(dt)
        assert next_dt == datetime(2024, 1, 16, 0, 0, 0)

    def test_get_next_day_month_rollover(self):
        """Test getting next day with month rollover."""
        dt = datetime(2024, 1, 31, 10, 30, 0)
        next_dt = get_next_day(dt)
        assert next_dt == datetime(2024, 2, 1, 0, 0, 0)

    def test_get_next_day_year_rollover(self):
        """Test getting next day with year rollover."""
        dt = datetime(2024, 12, 31, 10, 30, 0)
        next_dt = get_next_day(dt)
        assert next_dt == datetime(2025, 1, 1, 0, 0, 0)

    def test_get_next_month(self):
        """Test getting next month."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        next_dt = get_next_month(dt)
        assert next_dt == datetime(2024, 2, 1, 0, 0, 0)

    def test_get_next_month_year_rollover(self):
        """Test getting next month with year rollover."""
        dt = datetime(2024, 12, 15, 10, 30, 0)
        next_dt = get_next_month(dt)
        assert next_dt == datetime(2025, 1, 1, 0, 0, 0)

    def test_get_next_year(self):
        """Test getting next year."""
        dt = datetime(2024, 6, 15, 10, 30, 45)
        next_dt = get_next_year(dt)
        assert next_dt == datetime(2025, 1, 1, 0, 0, 0)


class TestCalendarFunctions:
    """Tests for calendar-related functions."""

    def test_get_days_in_month_january(self):
        """Test days in January."""
        assert get_days_in_month(2024, 1) == 31

    def test_get_days_in_month_february_non_leap(self):
        """Test days in February (non-leap year)."""
        assert get_days_in_month(2023, 2) == 28

    def test_get_days_in_month_february_leap(self):
        """Test days in February (leap year)."""
        assert get_days_in_month(2024, 2) == 29

    def test_get_days_in_month_april(self):
        """Test days in April."""
        assert get_days_in_month(2024, 4) == 30

    def test_is_leap_year_true(self):
        """Test leap year detection for leap years."""
        assert is_leap_year(2024) is True
        assert is_leap_year(2000) is True
        assert is_leap_year(2020) is True

    def test_is_leap_year_false(self):
        """Test leap year detection for non-leap years."""
        assert is_leap_year(2023) is False
        assert is_leap_year(1900) is False
        assert is_leap_year(2100) is False

    def test_get_weekday_sunday(self):
        """Test weekday for Sunday."""
        dt = datetime(2024, 1, 7)  # Sunday
        assert get_weekday(dt) == 0

    def test_get_weekday_monday(self):
        """Test weekday for Monday."""
        dt = datetime(2024, 1, 8)  # Monday
        assert get_weekday(dt) == 1

    def test_get_weekday_saturday(self):
        """Test weekday for Saturday."""
        dt = datetime(2024, 1, 6)  # Saturday
        assert get_weekday(dt) == 6

    def test_get_month_day_count(self):
        """Test getting day count for current month."""
        dt = datetime(2024, 2, 15)  # February in leap year
        assert get_month_day_count(dt) == 29


class TestDateTimeNormalization:
    """Tests for datetime normalization functions."""

    def test_normalize_datetime(self):
        """Test datetime normalization."""
        dt = datetime(2024, 1, 15, 10, 30, 45, 123456)
        normalized = normalize_datetime(dt)
        assert normalized == datetime(2024, 1, 15, 10, 30, 0, 0)

    def test_round_to_next_minute_no_rounding(self):
        """Test rounding when no rounding is needed."""
        dt = datetime(2024, 1, 15, 10, 30, 0, 0)
        rounded = round_to_next_minute(dt)
        assert rounded == dt

    def test_round_to_next_minute_with_seconds(self):
        """Test rounding with seconds."""
        dt = datetime(2024, 1, 15, 10, 30, 45, 0)
        rounded = round_to_next_minute(dt)
        assert rounded == datetime(2024, 1, 15, 10, 31, 0, 0)

    def test_round_to_next_minute_with_microseconds(self):
        """Test rounding with microseconds."""
        dt = datetime(2024, 1, 15, 10, 30, 0, 123456)
        rounded = round_to_next_minute(dt)
        assert rounded == datetime(2024, 1, 15, 10, 31, 0, 0)


class TestValidation:
    """Tests for validation functions."""

    def test_is_valid_day_in_month_valid(self):
        """Test valid days in month."""
        assert is_valid_day_in_month(2024, 1, 1) is True
        assert is_valid_day_in_month(2024, 1, 31) is True
        assert is_valid_day_in_month(2024, 2, 29) is True  # Leap year
        assert is_valid_day_in_month(2024, 4, 30) is True

    def test_is_valid_day_in_month_invalid(self):
        """Test invalid days in month."""
        assert is_valid_day_in_month(2024, 1, 0) is False
        assert is_valid_day_in_month(2024, 1, 32) is False
        assert is_valid_day_in_month(2023, 2, 29) is False  # Non-leap year
        assert is_valid_day_in_month(2024, 4, 31) is False

    def test_is_valid_day_in_month_invalid_month(self):
        """Test invalid month."""
        assert is_valid_day_in_month(2024, 0, 15) is False
        assert is_valid_day_in_month(2024, 13, 15) is False


class TestMonthOperations:
    """Tests for month increment/decrement operations."""

    def test_increment_month_normal(self):
        """Test incrementing month normally."""
        year, month = increment_month(2024, 5)
        assert year == 2024
        assert month == 6

    def test_increment_month_year_rollover(self):
        """Test incrementing month with year rollover."""
        year, month = increment_month(2024, 12)
        assert year == 2025
        assert month == 1

    def test_decrement_month_normal(self):
        """Test decrementing month normally."""
        year, month = decrement_month(2024, 5)
        assert year == 2024
        assert month == 4

    def test_decrement_month_year_rollover(self):
        """Test decrementing month with year rollover."""
        year, month = decrement_month(2024, 1)
        assert year == 2023
        assert month == 12


class TestBounds:
    """Tests for getting time period bounds."""

    def test_get_month_bounds(self):
        """Test getting month boundaries."""
        dt = datetime(2024, 2, 15, 10, 30, 45)
        first, last = get_month_bounds(dt)

        assert first == datetime(2024, 2, 1, 0, 0, 0, 0)
        assert last == datetime(2024, 2, 29, 23, 59, 59, 999999)

    def test_get_month_bounds_january(self):
        """Test getting January boundaries."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        first, last = get_month_bounds(dt)

        assert first == datetime(2024, 1, 1, 0, 0, 0, 0)
        assert last == datetime(2024, 1, 31, 23, 59, 59, 999999)

    def test_get_week_bounds_midweek(self):
        """Test getting week boundaries from midweek."""
        # Wednesday, January 10, 2024
        dt = datetime(2024, 1, 10, 10, 30, 45)
        first, last = get_week_bounds(dt)

        # Should be Sunday, January 7 to Saturday, January 13
        assert first == datetime(2024, 1, 7, 0, 0, 0, 0)
        assert last == datetime(2024, 1, 13, 23, 59, 59, 999999)

    def test_get_week_bounds_sunday(self):
        """Test getting week boundaries from Sunday."""
        # Sunday, January 7, 2024
        dt = datetime(2024, 1, 7, 10, 30, 45)
        first, last = get_week_bounds(dt)

        assert first == datetime(2024, 1, 7, 0, 0, 0, 0)
        assert last == datetime(2024, 1, 13, 23, 59, 59, 999999)

    def test_get_week_bounds_saturday(self):
        """Test getting week boundaries from Saturday."""
        # Saturday, January 6, 2024
        dt = datetime(2024, 1, 6, 10, 30, 45)
        first, last = get_week_bounds(dt)

        # Should be Sunday, December 31, 2023 to Saturday, January 6, 2024
        assert first == datetime(2023, 12, 31, 0, 0, 0, 0)
        assert last == datetime(2024, 1, 6, 23, 59, 59, 999999)