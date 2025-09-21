"""Tests for validation functions."""

import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.exceptions import InvalidCronExpression, ValidationError
from cronpal.validators import (
    validate_expression,
    validate_expression_format,
    validate_field_characters,
)


class TestValidateExpressionFormat:
    """Tests for validate_expression_format function."""

    def test_valid_five_field_expression(self):
        """Test valid 5-field expression."""
        result = validate_expression_format("0 0 * * *")
        assert result == ["0", "0", "*", "*", "*"]

    def test_empty_expression(self):
        """Test empty expression raises error."""
        with pytest.raises(InvalidCronExpression, match="Empty"):
            validate_expression_format("")

    def test_whitespace_only_expression(self):
        """Test whitespace-only expression raises error."""
        with pytest.raises(InvalidCronExpression, match="Empty"):
            validate_expression_format("   ")

    def test_too_few_fields(self):
        """Test expression with too few fields."""
        with pytest.raises(InvalidCronExpression, match="Invalid number of fields"):
            validate_expression_format("0 0 *")

    def test_too_many_fields(self):
        """Test expression with too many fields."""
        with pytest.raises(InvalidCronExpression, match="Invalid number of fields"):
            validate_expression_format("0 0 * * * *")

    def test_special_string_yearly(self):
        """Test @yearly special string."""
        result = validate_expression_format("@yearly")
        assert result == ["0", "0", "1", "1", "*"]

    def test_special_string_monthly(self):
        """Test @monthly special string."""
        result = validate_expression_format("@monthly")
        assert result == ["0", "0", "1", "*", "*"]

    def test_special_string_daily(self):
        """Test @daily special string."""
        result = validate_expression_format("@daily")
        assert result == ["0", "0", "*", "*", "*"]

    def test_special_string_hourly(self):
        """Test @hourly special string."""
        result = validate_expression_format("@hourly")
        assert result == ["0", "*", "*", "*", "*"]

    def test_special_string_reboot(self):
        """Test @reboot special string."""
        result = validate_expression_format("@reboot")
        assert result == ["@reboot"]

    def test_invalid_special_string(self):
        """Test invalid special string."""
        with pytest.raises(InvalidCronExpression, match="Unknown special string"):
            validate_expression_format("@invalid")

    def test_expression_with_extra_spaces(self):
        """Test expression with extra spaces between fields."""
        result = validate_expression_format("0  0   *    *     *")
        assert result == ["0", "0", "*", "*", "*"]


class TestValidateFieldCharacters:
    """Tests for validate_field_characters function."""

    def test_valid_numeric_field(self):
        """Test valid numeric field."""
        validate_field_characters("15", "minute")  # Should not raise

    def test_valid_wildcard(self):
        """Test valid wildcard field."""
        validate_field_characters("*", "hour")  # Should not raise

    def test_valid_range(self):
        """Test valid range field."""
        validate_field_characters("1-5", "day_of_month")  # Should not raise

    def test_valid_list(self):
        """Test valid list field."""
        validate_field_characters("1,3,5", "month")  # Should not raise

    def test_valid_step(self):
        """Test valid step field."""
        validate_field_characters("*/5", "minute")  # Should not raise

    def test_valid_complex(self):
        """Test valid complex field."""
        validate_field_characters("1-5,7,9-11", "hour")  # Should not raise

    def test_invalid_character(self):
        """Test invalid character in field."""
        with pytest.raises(ValidationError, match="Invalid characters"):
            validate_field_characters("1@5", "minute")

    def test_month_with_letters(self):
        """Test month field with letters."""
        validate_field_characters("JAN", "month")  # Should not raise

    def test_day_of_week_with_letters(self):
        """Test day_of_week field with letters."""
        validate_field_characters("MON-FRI", "day_of_week")  # Should not raise

    def test_minute_with_letters_invalid(self):
        """Test minute field with letters (invalid)."""
        with pytest.raises(ValidationError, match="Invalid characters"):
            validate_field_characters("JAN", "minute")


class TestValidateExpression:
    """Tests for validate_expression function."""

    def test_valid_expression(self):
        """Test valid expression."""
        assert validate_expression("0 0 * * *") is True

    def test_valid_complex_expression(self):
        """Test valid complex expression."""
        assert validate_expression("*/15 0-23 1,15 * MON-FRI") is True

    def test_valid_special_string(self):
        """Test valid special string."""
        assert validate_expression("@daily") is True

    def test_valid_reboot(self):
        """Test valid @reboot."""
        assert validate_expression("@reboot") is True

    def test_invalid_expression_format(self):
        """Test invalid expression format."""
        with pytest.raises(InvalidCronExpression):
            validate_expression("0 0 0")

    def test_invalid_characters(self):
        """Test expression with invalid characters."""
        with pytest.raises(ValidationError):
            validate_expression("0 0 * * $")