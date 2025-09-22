"""Tests for previous time calculation utilities."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.time_utils import (
    get_previous_day,
    get_previous_hour,
    get_previous_minute,
    get_previous_month,
    get_previous_year,
    round_to_previous_minute,
)


class TestPreviousTimeIncrements:
    """Tests for previous time increment functions."""

    def test_get_previous_minute(self):
        """Test getting previous minute."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        prev_dt = get_previous_minute(dt)
        assert prev_dt == datetime(2024, 1, 15, 10, 29, 45)

    def test_get_previous_minute_hour_rollover(self):
        """Test getting previous minute with hour rollover."""
        dt = datetime(2024, 1, 15, 10, 0, 0)
        prev_dt = get_previous_minute(dt)
        assert prev_dt == datetime(2024, 1, 15, 9, 59, 0)

    def test_get_previous_minute_day_rollover(self):
        """Test getting previous minute with day rollover."""
        dt = datetime(2024, 1, 15, 0, 0, 0)
        prev_dt = get_previous_minute(dt)
        assert prev_dt == datetime(2024, 1, 14, 23, 59, 0)

    def test_get_previous_hour(self):
        """Test getting previous hour."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        prev_dt = get_previous_hour(dt)
        assert prev_dt == datetime(2024, 1, 15, 9, 59, 0, 0)

    def test_get_previous_hour_day_rollover(self):
        """Test getting previous hour with day rollover."""
        dt = datetime(2024, 1, 15, 0, 30, 0)
        prev_dt = get_previous_hour(dt)
        assert prev_dt == datetime(2024, 1, 14, 23, 59, 0, 0)

    def test_get_previous_day(self):
        """Test getting previous day."""
        dt = datetime(2024, 1, 15, 10, 30, 45)
        prev_dt = get_previous_day(dt)
        assert prev_dt == datetime(2024, 1, 14, 23, 59, 0, 0)

    def test_get_previous_day_month_rollover(self):
        """Test getting previous day with month rollover."""
        dt = datetime(2024, 2, 1, 10, 30, 0)
        prev_dt = get_previous_day(dt)
        assert prev_dt == datetime(2024, 1, 31, 23, 59, 0, 0)

    def test_get_previous_day_year_rollover(self):
        """Test getting previous day with year rollover."""
        dt = datetime(2024, 1, 1, 10, 30, 0)
        prev_dt = get_previous_day(dt)
        assert prev_dt == datetime(2023, 12, 31, 23, 59, 0, 0)

    def test_get_previous_month(self):
        """Test getting previous month."""
        dt = datetime(2024, 3, 15, 10, 30, 45)
        prev_dt = get_previous_month(dt)
        assert prev_dt == datetime(2024, 2, 29, 23, 59, 0, 0)  # 2024 is leap year

    def test_get_previous_month_year_rollover(self):
        """Test getting previous month with year rollover."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        prev_dt = get_previous_month(dt)
        assert prev_dt == datetime(2023, 12, 31, 23, 59, 0, 0)

    def test_get_previous_month_different_days(self):
        """Test getting previous month when months have different day counts."""
        # From March to February (non-leap year)
        dt = datetime(2023, 3, 31, 10, 30, 0)
        prev_dt = get_previous_month(dt)
        assert prev_dt == datetime(2023, 2, 28, 23, 59, 0, 0)

    def test_get_previous_month_leap_year(self):
        """Test getting previous month in leap year."""
        # From March to February (leap year)
        dt = datetime(2024, 3, 31, 10, 30, 0)
        prev_dt = get_previous_month(dt)
        assert prev_dt == datetime(2024, 2, 29, 23, 59, 0, 0)

    def test_get_previous_year(self):
        """Test getting previous year."""
        dt = datetime(2024, 6, 15, 10, 30, 45)
        prev_dt = get_previous_year(dt)
        assert prev_dt == datetime(2023, 12, 31, 23, 59, 0, 0)

    def test_get_previous_year_from_january(self):
        """Test getting previous year from January."""
        dt = datetime(2024, 1, 1, 0, 0, 0)
        prev_dt = get_previous_year(dt)
        assert prev_dt == datetime(2023, 12, 31, 23, 59, 0, 0)


class TestRoundToPreviousMinute:
    """Tests for round_to_previous_minute function."""

    def test_round_to_previous_minute_no_change(self):
        """Test rounding when already on minute boundary."""
        dt = datetime(2024, 1, 15, 10, 30, 0, 0)
        rounded = round_to_previous_minute(dt)
        assert rounded == dt

    def test_round_to_previous_minute_with_seconds(self):
        """Test rounding with seconds."""
        dt = datetime(2024, 1, 15, 10, 30, 45, 0)
        rounded = round_to_previous_minute(dt)
        assert rounded == datetime(2024, 1, 15, 10, 30, 0, 0)

    def test_round_to_previous_minute_with_microseconds(self):
        """Test rounding with microseconds."""
        dt = datetime(2024, 1, 15, 10, 30, 0, 123456)
        rounded = round_to_previous_minute(dt)
        assert rounded == datetime(2024, 1, 15, 10, 30, 0, 0)

    def test_round_to_previous_minute_with_both(self):
        """Test rounding with both seconds and microseconds."""
        dt = datetime(2024, 1, 15, 10, 30, 45, 123456)
        rounded = round_to_previous_minute(dt)
        assert rounded == datetime(2024, 1, 15, 10, 30, 0, 0)


class TestBoundaryConditions:
    """Tests for boundary conditions in previous time functions."""

    def test_previous_minute_at_year_start(self):
        """Test previous minute at start of year."""
        dt = datetime(2024, 1, 1, 0, 0, 0)
        prev_dt = get_previous_minute(dt)
        assert prev_dt == datetime(2023, 12, 31, 23, 59, 0)

    def test_previous_hour_at_year_start(self):
        """Test previous hour at start of year."""
        dt = datetime(2024, 1, 1, 0, 30, 0)
        prev_dt = get_previous_hour(dt)
        assert prev_dt == datetime(2023, 12, 31, 23, 59, 0, 0)

    def test_previous_day_at_year_start(self):
        """Test previous day at start of year."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        prev_dt = get_previous_day(dt)
        assert prev_dt == datetime(2023, 12, 31, 23, 59, 0, 0)

    def test_previous_month_february_to_january_31(self):
        """Test previous month from February goes to January 31."""
        dt = datetime(2024, 2, 15, 10, 0, 0)
        prev_dt = get_previous_month(dt)
        assert prev_dt == datetime(2024, 1, 31, 23, 59, 0, 0)

    def test_previous_month_may_to_april(self):
        """Test previous month from May (31 days) to April (30 days)."""
        dt = datetime(2024, 5, 31, 10, 0, 0)
        prev_dt = get_previous_month(dt)
        assert prev_dt == datetime(2024, 4, 30, 23, 59, 0, 0)

    def test_previous_month_july_to_june(self):
        """Test previous month from July (31 days) to June (30 days)."""
        dt = datetime(2024, 7, 31, 10, 0, 0)
        prev_dt = get_previous_month(dt)
        assert prev_dt == datetime(2024, 6, 30, 23, 59, 0, 0)

    def test_previous_functions_preserve_time_components(self):
        """Test that previous functions preserve appropriate time components."""
        # Previous minute preserves seconds
        dt = datetime(2024, 1, 15, 10, 30, 45, 123456)
        prev_minute = get_previous_minute(dt)
        assert prev_minute.second == 45
        assert prev_minute.microsecond == 123456

        # Previous hour sets minute to 59, second to 0
        prev_hour = get_previous_hour(dt)
        assert prev_hour.minute == 59
        assert prev_hour.second == 0
        assert prev_hour.microsecond == 0

        # Previous day sets time to 23:59:00
        prev_day = get_previous_day(dt)
        assert prev_day.hour == 23
        assert prev_day.minute == 59
        assert prev_day.second == 0
        assert prev_day.microsecond == 0