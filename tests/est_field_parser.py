"""Tests for field parser."""

import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.exceptions import FieldError, ParseError
from cronpal.field_parser import FieldParser
from cronpal.models import FieldType


class TestParseMinute:
    """Tests for parsing minute field."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = FieldParser()

    def test_parse_single_minute(self):
        """Test parsing a single minute value."""
        field = self.parser.parse_minute("0")
        assert field.raw_value == "0"
        assert field.field_type == FieldType.MINUTE
        assert field.parsed_values == {0}

    def test_parse_minute_wildcard(self):
        """Test parsing minute wildcard."""
        field = self.parser.parse_minute("*")
        assert field.raw_value == "*"
        assert field.parsed_values == set(range(0, 60))
        assert len(field.parsed_values) == 60

    def test_parse_minute_range(self):
        """Test parsing minute range."""
        field = self.parser.parse_minute("0-5")
        assert field.parsed_values == {0, 1, 2, 3, 4, 5}

    def test_parse_minute_list(self):
        """Test parsing minute list."""
        field = self.parser.parse_minute("0,15,30,45")
        assert field.parsed_values == {0, 15, 30, 45}

    def test_parse_minute_step_wildcard(self):
        """Test parsing minute step with wildcard."""
        field = self.parser.parse_minute("*/15")
        assert field.parsed_values == {0, 15, 30, 45}

    def test_parse_minute_step_range(self):
        """Test parsing minute step with range."""
        field = self.parser.parse_minute("0-30/5")
        assert field.parsed_values == {0, 5, 10, 15, 20, 25, 30}

    def test_parse_minute_complex(self):
        """Test parsing complex minute expression."""
        field = self.parser.parse_minute("0-10,20,30-40/5")
        expected = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 35, 40}
        assert field.parsed_values == expected

    def test_parse_minute_max_value(self):
        """Test parsing maximum minute value."""
        field = self.parser.parse_minute("59")
        assert field.parsed_values == {59}

    def test_parse_minute_out_of_range_high(self):
        """Test parsing minute value too high."""
        with pytest.raises(FieldError, match="minute.*out of range"):
            self.parser.parse_minute("60")

    def test_parse_minute_out_of_range_low(self):
        """Test parsing negative minute value."""
        with pytest.raises(FieldError, match="minute.*out of range"):
            self.parser.parse_minute("-1")

    def test_parse_minute_invalid_range(self):
        """Test parsing invalid minute range."""
        with pytest.raises(FieldError, match="start.*>.*end"):
            self.parser.parse_minute("30-10")

    def test_parse_minute_invalid_step(self):
        """Test parsing invalid minute step."""
        with pytest.raises(FieldError, match="Step value must be positive"):
            self.parser.parse_minute("*/0")

    def test_parse_minute_non_numeric(self):
        """Test parsing non-numeric minute value."""
        with pytest.raises(FieldError, match="not a number"):
            self.parser.parse_minute("abc")

    def test_parse_minute_empty(self):
        """Test parsing empty minute field."""
        with pytest.raises(FieldError, match="Empty"):
            self.parser.parse_minute("")

    def test_parse_minute_malformed_range(self):
        """Test parsing malformed range."""
        with pytest.raises(FieldError, match="Invalid range"):
            self.parser.parse_minute("0-5-10")

    def test_parse_minute_malformed_step(self):
        """Test parsing malformed step."""
        with pytest.raises(FieldError, match="Invalid step"):
            self.parser.parse_minute("*/5/10")

    def test_parse_minute_step_from_single(self):
        """Test parsing step from single value."""
        field = self.parser.parse_minute("5/10")
        # Should give 5, 15, 25, 35, 45, 55
        assert field.parsed_values == {5, 15, 25, 35, 45, 55}

    def test_parse_minute_multiple_wildcards(self):
        """Test that multiple wildcards are handled."""
        field = self.parser.parse_minute("*,*")
        assert field.parsed_values == set(range(0, 60))

    def test_parse_minute_duplicates_removed(self):
        """Test that duplicate values are removed."""
        field = self.parser.parse_minute("0,0,1,1,2")
        assert field.parsed_values == {0, 1, 2}

    def test_parse_minute_whitespace(self):
        """Test parsing with whitespace in list."""
        field = self.parser.parse_minute("0, 15, 30, 45")
        assert field.parsed_values == {0, 15, 30, 45}


class TestParseHour:
    """Tests for parsing hour field."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = FieldParser()

    def test_parse_single_hour(self):
        """Test parsing a single hour value."""
        field = self.parser.parse_hour("0")
        assert field.raw_value == "0"
        assert field.field_type == FieldType.HOUR
        assert field.parsed_values == {0}

    def test_parse_hour_wildcard(self):
        """Test parsing hour wildcard."""
        field = self.parser.parse_hour("*")
        assert field.raw_value == "*"
        assert field.parsed_values == set(range(0, 24))
        assert len(field.parsed_values) == 24

    def test_parse_hour_range(self):
        """Test parsing hour range."""
        field = self.parser.parse_hour("9-17")
        assert field.parsed_values == {9, 10, 11, 12, 13, 14, 15, 16, 17}

    def test_parse_hour_list(self):
        """Test parsing hour list."""
        field = self.parser.parse_hour("0,6,12,18")
        assert field.parsed_values == {0, 6, 12, 18}

    def test_parse_hour_step_wildcard(self):
        """Test parsing hour step with wildcard."""
        field = self.parser.parse_hour("*/4")
        assert field.parsed_values == {0, 4, 8, 12, 16, 20}

    def test_parse_hour_step_range(self):
        """Test parsing hour step with range."""
        field = self.parser.parse_hour("8-18/2")
        assert field.parsed_values == {8, 10, 12, 14, 16, 18}

    def test_parse_hour_complex(self):
        """Test parsing complex hour expression."""
        field = self.parser.parse_hour("0-6,12,18-23/2")
        expected = {0, 1, 2, 3, 4, 5, 6, 12, 18, 20, 22}
        assert field.parsed_values == expected

    def test_parse_hour_max_value(self):
        """Test parsing maximum hour value."""
        field = self.parser.parse_hour("23")
        assert field.parsed_values == {23}

    def test_parse_hour_out_of_range_high(self):
        """Test parsing hour value too high."""
        with pytest.raises(FieldError, match="hour.*out of range"):
            self.parser.parse_hour("24")

    def test_parse_hour_out_of_range_low(self):
        """Test parsing negative hour value."""
        with pytest.raises(FieldError, match="hour.*out of range"):
            self.parser.parse_hour("-1")

    def test_parse_hour_invalid_range(self):
        """Test parsing invalid hour range."""
        with pytest.raises(FieldError, match="start.*>.*end"):
            self.parser.parse_hour("20-10")

    def test_parse_hour_invalid_step(self):
        """Test parsing invalid hour step."""
        with pytest.raises(FieldError, match="Step value must be positive"):
            self.parser.parse_hour("*/0")

    def test_parse_hour_non_numeric(self):
        """Test parsing non-numeric hour value."""
        with pytest.raises(FieldError, match="not a number"):
            self.parser.parse_hour("noon")

    def test_parse_hour_empty(self):
        """Test parsing empty hour field."""
        with pytest.raises(FieldError, match="Empty"):
            self.parser.parse_hour("")

    def test_parse_hour_business_hours(self):
        """Test parsing typical business hours."""
        field = self.parser.parse_hour("9-17")
        assert field.parsed_values == {9, 10, 11, 12, 13, 14, 15, 16, 17}

    def test_parse_hour_every_two_hours(self):
        """Test parsing every two hours."""
        field = self.parser.parse_hour("*/2")
        assert field.parsed_values == {0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22}

    def test_parse_hour_night_shift(self):
        """Test parsing night shift hours."""
        field = self.parser.parse_hour("22,23,0,1,2,3,4,5,6")
        assert field.parsed_values == {0, 1, 2, 3, 4, 5, 6, 22, 23}

    def test_parse_hour_step_from_single(self):
        """Test parsing step from single hour value."""
        field = self.parser.parse_hour("8/3")
        # Should give 8, 11, 14, 17, 20, 23
        assert field.parsed_values == {8, 11, 14, 17, 20, 23}

    def test_parse_hour_duplicates_removed(self):
        """Test that duplicate hour values are removed."""
        field = self.parser.parse_hour("0,0,12,12")
        assert field.parsed_values == {0, 12}


class TestParseDayOfMonth:
    """Tests for parsing day of month field."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = FieldParser()

    def test_parse_single_day(self):
        """Test parsing a single day value."""
        field = self.parser.parse_day_of_month("1")
        assert field.raw_value == "1"
        assert field.field_type == FieldType.DAY_OF_MONTH
        assert field.parsed_values == {1}

    def test_parse_day_wildcard(self):
        """Test parsing day wildcard."""
        field = self.parser.parse_day_of_month("*")
        assert field.raw_value == "*"
        assert field.parsed_values == set(range(1, 32))
        assert len(field.parsed_values) == 31

    def test_parse_day_range(self):
        """Test parsing day range."""
        field = self.parser.parse_day_of_month("1-7")
        assert field.parsed_values == {1, 2, 3, 4, 5, 6, 7}

    def test_parse_day_list(self):
        """Test parsing day list."""
        field = self.parser.parse_day_of_month("1,15,31")
        assert field.parsed_values == {1, 15, 31}

    def test_parse_day_step_wildcard(self):
        """Test parsing day step with wildcard."""
        field = self.parser.parse_day_of_month("*/5")
        assert field.parsed_values == {1, 6, 11, 16, 21, 26, 31}

    def test_parse_day_step_range(self):
        """Test parsing day step with range."""
        field = self.parser.parse_day_of_month("1-15/3")
        assert field.parsed_values == {1, 4, 7, 10, 13}

    def test_parse_day_complex(self):
        """Test parsing complex day expression."""
        field = self.parser.parse_day_of_month("1-5,15,20-25/2")
        expected = {1, 2, 3, 4, 5, 15, 20, 22, 24}
        assert field.parsed_values == expected

    def test_parse_day_max_value(self):
        """Test parsing maximum day value."""
        field = self.parser.parse_day_of_month("31")
        assert field.parsed_values == {31}

    def test_parse_day_out_of_range_high(self):
        """Test parsing day value too high."""
        with pytest.raises(FieldError, match="day of month.*out of range"):
            self.parser.parse_day_of_month("32")

    def test_parse_day_out_of_range_low(self):
        """Test parsing day value too low."""
        with pytest.raises(FieldError, match="day of month.*out of range"):
            self.parser.parse_day_of_month("0")

    def test_parse_day_invalid_range(self):
        """Test parsing invalid day range."""
        with pytest.raises(FieldError, match="start.*>.*end"):
            self.parser.parse_day_of_month("20-10")

    def test_parse_day_invalid_step(self):
        """Test parsing invalid day step."""
        with pytest.raises(FieldError, match="Step value must be positive"):
            self.parser.parse_day_of_month("*/0")

    def test_parse_day_non_numeric(self):
        """Test parsing non-numeric day value."""
        with pytest.raises(FieldError, match="not a number"):
            self.parser.parse_day_of_month("first")

    def test_parse_day_empty(self):
        """Test parsing empty day field."""
        with pytest.raises(FieldError, match="Empty"):
            self.parser.parse_day_of_month("")

    def test_parse_day_first_week(self):
        """Test parsing first week of month."""
        field = self.parser.parse_day_of_month("1-7")
        assert field.parsed_values == {1, 2, 3, 4, 5, 6, 7}

    def test_parse_day_biweekly(self):
        """Test parsing bi-weekly pattern."""
        field = self.parser.parse_day_of_month("1,15")
        assert field.parsed_values == {1, 15}

    def test_parse_day_every_other_day(self):
        """Test parsing every other day."""
        field = self.parser.parse_day_of_month("*/2")
        expected = {1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31}
        assert field.parsed_values == expected

    def test_parse_day_step_from_single(self):
        """Test parsing step from single day value."""
        field = self.parser.parse_day_of_month("5/5")
        # Should give 5, 10, 15, 20, 25, 30
        assert field.parsed_values == {5, 10, 15, 20, 25, 30}

    def test_parse_day_end_of_month(self):
        """Test parsing end of month days."""
        field = self.parser.parse_day_of_month("28-31")
        assert field.parsed_values == {28, 29, 30, 31}

    def test_parse_day_duplicates_removed(self):
        """Test that duplicate day values are removed."""
        field = self.parser.parse_day_of_month("1,1,15,15")
        assert field.parsed_values == {1, 15}


class TestFieldParserInternals:
    """Tests for internal parsing methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = FieldParser()
        from cronpal.models import FIELD_RANGES
        self.minute_range = FIELD_RANGES[FieldType.MINUTE]
        self.hour_range = FIELD_RANGES[FieldType.HOUR]
        self.day_range = FIELD_RANGES[FieldType.DAY_OF_MONTH]

    def test_parse_single_valid(self):
        """Test _parse_single with valid value."""
        result = self.parser._parse_single("30", self.minute_range, "minute")
        assert result == 30

    def test_parse_single_boundary_min(self):
        """Test _parse_single at minimum boundary."""
        result = self.parser._parse_single("0", self.minute_range, "minute")
        assert result == 0

    def test_parse_single_boundary_max(self):
        """Test _parse_single at maximum boundary."""
        result = self.parser._parse_single("59", self.minute_range, "minute")
        assert result == 59

    def test_parse_range_valid(self):
        """Test _parse_range with valid range."""
        result = self.parser._parse_range("10-20", self.minute_range, "minute")
        assert result == set(range(10, 21))

    def test_parse_range_single_span(self):
        """Test _parse_range with single value span."""
        result = self.parser._parse_range("15-15", self.minute_range, "minute")
        assert result == {15}

    def test_parse_step_every_n(self):
        """Test _parse_step with every N pattern."""
        result = self.parser._parse_step("*/10", self.minute_range, "minute")
        assert result == {0, 10, 20, 30, 40, 50}

    def test_parse_step_range_with_step(self):
        """Test _parse_step with range and step."""
        result = self.parser._parse_step("5-25/5", self.minute_range, "minute")
        assert result == {5, 10, 15, 20, 25}

    def test_parse_field_empty_string(self):
        """Test _parse_field with empty string."""
        with pytest.raises(ParseError, match="Empty"):
            self.parser._parse_field("", self.minute_range, "minute")

    def test_parse_field_wildcard_only(self):
        """Test _parse_field with wildcard."""
        result = self.parser._parse_field("*", self.minute_range, "minute")
        assert result == set(range(0, 60))
        assert len(result) == 60

    def test_hour_range_boundaries(self):
        """Test hour range boundaries."""
        result = self.parser._parse_field("*", self.hour_range, "hour")
        assert min(result) == 0
        assert max(result) == 23
        assert len(result) == 24

    def test_day_range_boundaries(self):
        """Test day of month range boundaries."""
        result = self.parser._parse_field("*", self.day_range, "day")
        assert min(result) == 1
        assert max(result) == 31
        assert len(result) == 31