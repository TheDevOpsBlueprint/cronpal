"""Tests for special string parser."""

import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.exceptions import InvalidCronExpression
from cronpal.special_parser import SpecialStringParser


class TestSpecialStringParser:
    """Tests for SpecialStringParser class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = SpecialStringParser()

    def test_is_special_string_yearly(self):
        """Test detecting @yearly as special string."""
        assert self.parser.is_special_string("@yearly") is True
        assert self.parser.is_special_string("@YEARLY") is True
        assert self.parser.is_special_string("@Yearly") is True

    def test_is_special_string_annually(self):
        """Test detecting @annually as special string."""
        assert self.parser.is_special_string("@annually") is True
        assert self.parser.is_special_string("@ANNUALLY") is True

    def test_is_special_string_monthly(self):
        """Test detecting @monthly as special string."""
        assert self.parser.is_special_string("@monthly") is True
        assert self.parser.is_special_string("@MONTHLY") is True

    def test_is_special_string_weekly(self):
        """Test detecting @weekly as special string."""
        assert self.parser.is_special_string("@weekly") is True
        assert self.parser.is_special_string("@WEEKLY") is True

    def test_is_special_string_daily(self):
        """Test detecting @daily as special string."""
        assert self.parser.is_special_string("@daily") is True
        assert self.parser.is_special_string("@DAILY") is True

    def test_is_special_string_midnight(self):
        """Test detecting @midnight as special string."""
        assert self.parser.is_special_string("@midnight") is True
        assert self.parser.is_special_string("@MIDNIGHT") is True

    def test_is_special_string_hourly(self):
        """Test detecting @hourly as special string."""
        assert self.parser.is_special_string("@hourly") is True
        assert self.parser.is_special_string("@HOURLY") is True

    def test_is_special_string_reboot(self):
        """Test detecting @reboot as special string."""
        assert self.parser.is_special_string("@reboot") is True
        assert self.parser.is_special_string("@REBOOT") is True

    def test_is_special_string_with_spaces(self):
        """Test detecting special strings with leading/trailing spaces."""
        assert self.parser.is_special_string("  @daily  ") is True
        assert self.parser.is_special_string("\t@weekly\n") is True

    def test_is_not_special_string(self):
        """Test strings that are not special."""
        assert self.parser.is_special_string("0 0 * * *") is False
        assert self.parser.is_special_string("@invalid") is False
        assert self.parser.is_special_string("daily") is False
        assert self.parser.is_special_string("@@daily") is False

    def test_parse_yearly(self):
        """Test parsing @yearly."""
        expr = self.parser.parse("@yearly")
        assert expr.raw_expression == "@yearly"
        assert expr.minute.parsed_values == {0}
        assert expr.hour.parsed_values == {0}
        assert expr.day_of_month.parsed_values == {1}
        assert expr.month.parsed_values == {1}
        assert expr.day_of_week.parsed_values == set(range(0, 7))

    def test_parse_annually(self):
        """Test parsing @annually."""
        expr = self.parser.parse("@annually")
        assert expr.raw_expression == "@annually"
        assert expr.minute.parsed_values == {0}
        assert expr.hour.parsed_values == {0}
        assert expr.day_of_month.parsed_values == {1}
        assert expr.month.parsed_values == {1}
        assert expr.day_of_week.parsed_values == set(range(0, 7))

    def test_parse_monthly(self):
        """Test parsing @monthly."""
        expr = self.parser.parse("@monthly")
        assert expr.raw_expression == "@monthly"
        assert expr.minute.parsed_values == {0}
        assert expr.hour.parsed_values == {0}
        assert expr.day_of_month.parsed_values == {1}
        assert expr.month.parsed_values == set(range(1, 13))
        assert expr.day_of_week.parsed_values == set(range(0, 7))

    def test_parse_weekly(self):
        """Test parsing @weekly."""
        expr = self.parser.parse("@weekly")
        assert expr.raw_expression == "@weekly"
        assert expr.minute.parsed_values == {0}
        assert expr.hour.parsed_values == {0}
        assert expr.day_of_month.parsed_values == set(range(1, 32))
        assert expr.month.parsed_values == set(range(1, 13))
        assert expr.day_of_week.parsed_values == {0}

    def test_parse_daily(self):
        """Test parsing @daily."""
        expr = self.parser.parse("@daily")
        assert expr.raw_expression == "@daily"
        assert expr.minute.parsed_values == {0}
        assert expr.hour.parsed_values == {0}
        assert expr.day_of_month.parsed_values == set(range(1, 32))
        assert expr.month.parsed_values == set(range(1, 13))
        assert expr.day_of_week.parsed_values == set(range(0, 7))

    def test_parse_midnight(self):
        """Test parsing @midnight."""
        expr = self.parser.parse("@midnight")
        assert expr.raw_expression == "@midnight"
        assert expr.minute.parsed_values == {0}
        assert expr.hour.parsed_values == {0}
        assert expr.day_of_month.parsed_values == set(range(1, 32))
        assert expr.month.parsed_values == set(range(1, 13))
        assert expr.day_of_week.parsed_values == set(range(0, 7))

    def test_parse_hourly(self):
        """Test parsing @hourly."""
        expr = self.parser.parse("@hourly")
        assert expr.raw_expression == "@hourly"
        assert expr.minute.parsed_values == {0}
        assert expr.hour.parsed_values == set(range(0, 24))
        assert expr.day_of_month.parsed_values == set(range(1, 32))
        assert expr.month.parsed_values == set(range(1, 13))
        assert expr.day_of_week.parsed_values == set(range(0, 7))

    def test_parse_reboot(self):
        """Test parsing @reboot."""
        expr = self.parser.parse("@reboot")
        assert expr.raw_expression == "@reboot"
        # @reboot doesn't have time fields
        assert expr.minute is None
        assert expr.hour is None
        assert expr.day_of_month is None
        assert expr.month is None
        assert expr.day_of_week is None

    def test_parse_case_insensitive(self):
        """Test parsing with different cases."""
        expr1 = self.parser.parse("@DAILY")
        assert expr1.raw_expression in ["@daily", "@DAILY"]
        assert expr1.minute.parsed_values == {0}
        assert expr1.hour.parsed_values == {0}

        expr2 = self.parser.parse("@Daily")
        assert expr2.raw_expression in ["@daily", "@Daily", "@DAILY"]
        assert expr2.minute.parsed_values == {0}
        assert expr2.hour.parsed_values == {0}

    def test_parse_invalid_special_string(self):
        """Test parsing invalid special string."""
        with pytest.raises(InvalidCronExpression, match="Unknown special string"):
            self.parser.parse("@invalid")

        with pytest.raises(InvalidCronExpression, match="Unknown special string"):
            self.parser.parse("@notathing")

    def test_parse_with_whitespace(self):
        """Test parsing special strings with whitespace."""
        expr = self.parser.parse("  @daily  ")
        assert expr.raw_expression in ["@daily", "  @daily  "]
        assert expr.minute.parsed_values == {0}

    def test_get_description_yearly(self):
        """Test description for @yearly."""
        desc = self.parser.get_description("@yearly")
        assert "once a year" in desc.lower()
        assert "january 1" in desc.lower()

    def test_get_description_annually(self):
        """Test description for @annually."""
        desc = self.parser.get_description("@annually")
        assert "once a year" in desc.lower()
        assert "january 1" in desc.lower()

    def test_get_description_monthly(self):
        """Test description for @monthly."""
        desc = self.parser.get_description("@monthly")
        assert "once a month" in desc.lower()
        assert "1st" in desc.lower()

    def test_get_description_weekly(self):
        """Test description for @weekly."""
        desc = self.parser.get_description("@weekly")
        assert "once a week" in desc.lower()
        assert "sunday" in desc.lower()

    def test_get_description_daily(self):
        """Test description for @daily."""
        desc = self.parser.get_description("@daily")
        assert "once a day" in desc.lower()
        assert "midnight" in desc.lower()

    def test_get_description_midnight(self):
        """Test description for @midnight."""
        desc = self.parser.get_description("@midnight")
        assert "once a day" in desc.lower()
        assert "midnight" in desc.lower()

    def test_get_description_hourly(self):
        """Test description for @hourly."""
        desc = self.parser.get_description("@hourly")
        assert "once an hour" in desc.lower() or "once a hour" in desc.lower()
        assert "beginning of the hour" in desc.lower()

    def test_get_description_reboot(self):
        """Test description for @reboot."""
        desc = self.parser.get_description("@reboot")
        assert "startup" in desc.lower() or "reboot" in desc.lower()

    def test_get_description_invalid(self):
        """Test description for invalid special string."""
        desc = self.parser.get_description("@invalid")
        assert "unknown" in desc.lower()

    def test_get_description_case_insensitive(self):
        """Test description with different cases."""
        desc1 = self.parser.get_description("@DAILY")
        desc2 = self.parser.get_description("@daily")
        desc3 = self.parser.get_description("@Daily")

        # All should return the same description
        assert desc1 == desc2
        assert desc2 == desc3