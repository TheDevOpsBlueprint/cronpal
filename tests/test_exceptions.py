"""Tests for custom exceptions."""

import sys
from pathlib import Path

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.exceptions import (
    CronPalError,
    FieldError,
    InvalidCronExpression,
    ParseError,
    ValidationError,
)


def test_cronpal_error_base():
    """Test CronPalError base exception."""
    error = CronPalError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_invalid_cron_expression():
    """Test InvalidCronExpression."""
    error = InvalidCronExpression("Invalid format")
    assert str(error) == "Invalid format"
    assert isinstance(error, CronPalError)


def test_validation_error():
    """Test ValidationError."""
    error = ValidationError("Validation failed")
    assert str(error) == "Validation failed"
    assert isinstance(error, CronPalError)


def test_parse_error():
    """Test ParseError."""
    error = ParseError("Parse failed")
    assert str(error) == "Parse failed"
    assert isinstance(error, CronPalError)


def test_field_error():
    """Test FieldError with field name."""
    error = FieldError("minute", "Invalid value")
    assert str(error) == "minute: Invalid value"
    assert error.field_name == "minute"
    assert isinstance(error, CronPalError)


def test_raising_exceptions():
    """Test that exceptions can be raised properly."""
    with pytest.raises(CronPalError):
        raise CronPalError("Test")

    with pytest.raises(InvalidCronExpression):
        raise InvalidCronExpression("Test")

    with pytest.raises(ValidationError):
        raise ValidationError("Test")

    with pytest.raises(ParseError):
        raise ParseError("Test")

    with pytest.raises(FieldError):
        raise FieldError("hour", "Test")


def test_exception_hierarchy():
    """Test that all exceptions inherit from CronPalError."""
    assert issubclass(InvalidCronExpression, CronPalError)
    assert issubclass(ValidationError, CronPalError)
    assert issubclass(ParseError, CronPalError)
    assert issubclass(FieldError, CronPalError)