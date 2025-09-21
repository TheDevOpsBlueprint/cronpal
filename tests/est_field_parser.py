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


class TestFieldParserInternals:
    """Tests for internal parsing methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = FieldParser()
        from cronpal.models import FIELD_RANGES
        self.minute_range = FIELD_RANGES[FieldType.MINUTE]

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