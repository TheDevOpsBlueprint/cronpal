"""Tests for timezone utilities."""

import sys
from datetime import datetime
from pathlib import Path

import pytest
import pytz

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.timezone_utils import (
    convert_between_timezones,
    convert_to_timezone,
    format_datetime_with_timezone,
    get_current_time,
    get_timezone,
    get_timezone_abbreviation,
    get_timezone_offset,
    is_valid_timezone,
    list_common_timezones,
    localize_datetime,
)


class TestGetTimezone:
    """Tests for get_timezone function."""

    def test_get_timezone_utc(self):
        """Test getting UTC timezone."""
        tz = get_timezone("UTC")
        assert tz == pytz.UTC

    def test_get_timezone_us_eastern(self):
        """Test getting US/Eastern timezone."""
        tz = get_timezone("US/Eastern")
        assert tz.zone == "US/Eastern"

    def test_get_timezone_europe_london(self):
        """Test getting Europe/London timezone."""
        tz = get_timezone("Europe/London")
        assert tz.zone == "Europe/London"

    def test_get_timezone_invalid(self):
        """Test getting invalid timezone."""
        with pytest.raises(ValueError, match="Unknown timezone"):
            get_timezone("Invalid/Timezone")

    def test_get_timezone_none_returns_default(self):
        """Test getting timezone with None returns a timezone."""
        tz = get_timezone(None)
        assert tz is not None
        # Should be either local timezone or UTC


class TestConvertToTimezone:
    """Tests for convert_to_timezone function."""

    def test_convert_naive_to_utc(self):
        """Test converting naive datetime to UTC."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = convert_to_timezone(dt, "UTC")

        assert result.tzinfo == pytz.UTC
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30

    def test_convert_aware_to_different_timezone(self):
        """Test converting aware datetime to different timezone."""
        # Create UTC datetime
        dt = pytz.UTC.localize(datetime(2024, 1, 15, 10, 30, 0))

        # Convert to US/Eastern (UTC-5 in January)
        result = convert_to_timezone(dt, "US/Eastern")

        assert result.tzinfo.zone == "US/Eastern"
        assert result.hour == 5  # 10:30 UTC -> 5:30 EST

    def test_convert_with_timezone_object(self):
        """Test converting with timezone object instead of string."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        tz = pytz.timezone("Europe/London")

        result = convert_to_timezone(dt, tz)
        assert result.tzinfo.zone == "Europe/London"


class TestLocalizeDateTime:
    """Tests for localize_datetime function."""

    def test_localize_naive_datetime(self):
        """Test localizing naive datetime."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = localize_datetime(dt, "US/Pacific")

        assert result.tzinfo.zone == "US/Pacific"
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 10
        assert result.minute == 30

    def test_localize_already_aware_raises_error(self):
        """Test localizing already aware datetime raises error."""
        dt = pytz.UTC.localize(datetime(2024, 1, 15, 10, 30, 0))

        with pytest.raises(ValueError, match="already timezone-aware"):
            localize_datetime(dt, "US/Eastern")

    def test_localize_with_timezone_object(self):
        """Test localizing with timezone object."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        tz = pytz.timezone("Asia/Tokyo")

        result = localize_datetime(dt, tz)
        assert result.tzinfo.zone == "Asia/Tokyo"


class TestGetCurrentTime:
    """Tests for get_current_time function."""

    def test_get_current_time_utc(self):
        """Test getting current time in UTC."""
        result = get_current_time("UTC")
        assert result.tzinfo == pytz.UTC
        assert isinstance(result, datetime)

    def test_get_current_time_with_timezone(self):
        """Test getting current time with specific timezone."""
        result = get_current_time("US/Eastern")
        assert result.tzinfo.zone == "US/Eastern"

    def test_get_current_time_none(self):
        """Test getting current time with None timezone."""
        result = get_current_time(None)
        assert result.tzinfo is not None

    def test_get_current_time_with_timezone_object(self):
        """Test getting current time with timezone object."""
        tz = pytz.timezone("Europe/Paris")
        result = get_current_time(tz)
        assert result.tzinfo.zone == "Europe/Paris"


class TestListCommonTimezones:
    """Tests for list_common_timezones function."""

    def test_list_common_timezones_returns_list(self):
        """Test that function returns a list."""
        result = list_common_timezones()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_list_common_timezones_contains_major_zones(self):
        """Test that list contains major timezones."""
        result = list_common_timezones()
        assert "UTC" in result
        assert "US/Eastern" in result
        assert "Europe/London" in result
        assert "Asia/Tokyo" in result


class TestIsValidTimezone:
    """Tests for is_valid_timezone function."""

    def test_is_valid_timezone_true(self):
        """Test valid timezone names."""
        assert is_valid_timezone("UTC") is True
        assert is_valid_timezone("US/Eastern") is True
        assert is_valid_timezone("Europe/London") is True
        assert is_valid_timezone("Asia/Shanghai") is True

    def test_is_valid_timezone_false(self):
        """Test invalid timezone names."""
        assert is_valid_timezone("Invalid") is False
        assert is_valid_timezone("US/Invalid") is False
        assert is_valid_timezone("NotATimezone") is False


class TestGetTimezoneOffset:
    """Tests for get_timezone_offset function."""

    def test_get_timezone_offset_utc(self):
        """Test UTC offset."""
        dt = datetime(2024, 1, 15, 10, 0, 0)
        result = get_timezone_offset("UTC", dt)
        assert result == "+00:00"

    def test_get_timezone_offset_eastern_winter(self):
        """Test Eastern timezone offset in winter."""
        dt = datetime(2024, 1, 15, 10, 0, 0)  # January - EST
        result = get_timezone_offset("US/Eastern", dt)
        assert result == "-05:00"

    def test_get_timezone_offset_eastern_summer(self):
        """Test Eastern timezone offset in summer."""
        dt = datetime(2024, 7, 15, 10, 0, 0)  # July - EDT
        result = get_timezone_offset("US/Eastern", dt)
        assert result == "-04:00"

    def test_get_timezone_offset_with_timezone_object(self):
        """Test offset with timezone object."""
        tz = pytz.timezone("Asia/Tokyo")
        dt = datetime(2024, 1, 15, 10, 0, 0)
        result = get_timezone_offset(tz, dt)
        assert result == "+09:00"


class TestGetTimezoneAbbreviation:
    """Tests for get_timezone_abbreviation function."""

    def test_get_timezone_abbreviation_utc(self):
        """Test UTC abbreviation."""
        dt = datetime(2024, 1, 15, 10, 0, 0)
        result = get_timezone_abbreviation("UTC", dt)
        assert result == "UTC"

    def test_get_timezone_abbreviation_eastern_winter(self):
        """Test Eastern timezone abbreviation in winter."""
        dt = datetime(2024, 1, 15, 10, 0, 0)  # January - EST
        result = get_timezone_abbreviation("US/Eastern", dt)
        assert result == "EST"

    def test_get_timezone_abbreviation_eastern_summer(self):
        """Test Eastern timezone abbreviation in summer."""
        dt = datetime(2024, 7, 15, 10, 0, 0)  # July - EDT
        result = get_timezone_abbreviation("US/Eastern", dt)
        assert result == "EDT"

    def test_get_timezone_abbreviation_with_timezone_object(self):
        """Test abbreviation with timezone object."""
        tz = pytz.timezone("Europe/London")
        dt = datetime(2024, 1, 15, 10, 0, 0)
        result = get_timezone_abbreviation(tz, dt)
        assert result in ["GMT", "BST"]


class TestFormatDatetimeWithTimezone:
    """Tests for format_datetime_with_timezone function."""

    def test_format_datetime_naive_with_timezone(self):
        """Test formatting naive datetime with timezone."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = format_datetime_with_timezone(dt, "US/Eastern")

        assert "2024-01-15 10:30:00" in result
        assert "Monday" in result
        assert "EST" in result
        assert "(-05:00)" in result

    def test_format_datetime_aware(self):
        """Test formatting aware datetime."""
        dt = pytz.UTC.localize(datetime(2024, 1, 15, 10, 30, 0))
        result = format_datetime_with_timezone(dt)

        assert "2024-01-15 10:30:00" in result
        assert "UTC" in result
        assert "(+00:00)" in result

    def test_format_datetime_convert_timezone(self):
        """Test formatting with timezone conversion."""
        dt = pytz.UTC.localize(datetime(2024, 1, 15, 10, 30, 0))
        result = format_datetime_with_timezone(dt, "US/Eastern")

        assert "2024-01-15 05:30:00" in result  # Converted to EST
        assert "EST" in result


class TestConvertBetweenTimezones:
    """Tests for convert_between_timezones function."""

    def test_convert_between_timezones_naive(self):
        """Test converting naive datetime between timezones."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        result = convert_between_timezones(dt, "UTC", "US/Eastern")

        assert result.tzinfo.zone == "US/Eastern"
        assert result.hour == 5  # 10:30 UTC -> 5:30 EST

    def test_convert_between_timezones_aware(self):
        """Test converting aware datetime between timezones."""
        # Create datetime already in UTC
        dt = pytz.UTC.localize(datetime(2024, 1, 15, 10, 30, 0))
        result = convert_between_timezones(dt, "UTC", "US/Eastern")

        assert result.tzinfo.zone == "US/Eastern"
        assert result.hour == 5

    def test_convert_between_timezones_with_objects(self):
        """Test converting with timezone objects."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        from_tz = pytz.timezone("Europe/London")
        to_tz = pytz.timezone("Asia/Tokyo")

        result = convert_between_timezones(dt, from_tz, to_tz)
        assert result.tzinfo.zone == "Asia/Tokyo"
        assert result.hour == 19  # 10:30 GMT -> 19:30 JST

    def test_convert_between_timezones_dst(self):
        """Test converting between timezones with DST."""
        # Summer date for DST
        dt = datetime(2024, 7, 15, 10, 30, 0)
        result = convert_between_timezones(dt, "UTC", "US/Eastern")

        assert result.tzinfo.zone == "US/Eastern"
        assert result.hour == 6  # 10:30 UTC -> 6:30 EDT (DST)