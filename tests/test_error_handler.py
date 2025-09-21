"""Tests for error handler module."""

import sys
from pathlib import Path
from io import StringIO

import pytest

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cronpal.error_handler import ErrorHandler, suggest_fix
from cronpal.exceptions import (
    CronPalError,
    FieldError,
    InvalidCronExpression,
    ParseError,
    ValidationError,
)


class TestErrorHandler:
    """Tests for ErrorHandler class."""

    def test_initialization(self):
        """Test ErrorHandler initialization."""
        handler = ErrorHandler()
        assert handler.verbose is False
        assert handler.error_count == 0

        handler_verbose = ErrorHandler(verbose=True)
        assert handler_verbose.verbose is True

    def test_handle_invalid_expression(self):
        """Test handling InvalidCronExpression."""
        handler = ErrorHandler()
        error = InvalidCronExpression("Too few fields")
        message = handler.handle_error(error)

        assert "✗ Invalid cron expression" in message
        assert "Too few fields" in message
        assert handler.error_count == 1

    def test_handle_invalid_expression_verbose(self):
        """Test handling InvalidCronExpression with verbose mode."""
        handler = ErrorHandler(verbose=True)
        error = InvalidCronExpression("Too few fields")
        message = handler.handle_error(error, "0 0 *")

        assert "✗ Invalid cron expression" in message
        assert "Expression: '0 0 *'" in message
        assert "Expected format:" in message

    def test_handle_field_error(self):
        """Test handling FieldError."""
        handler = ErrorHandler()
        error = FieldError("minute", "Value out of range")
        message = handler.handle_error(error)

        assert "✗ Field error in minute" in message
        assert "Value out of range" in message

    def test_handle_validation_error(self):
        """Test handling ValidationError."""
        handler = ErrorHandler()
        error = ValidationError("Invalid characters")
        message = handler.handle_error(error)

        assert "✗ Validation failed" in message
        assert "Invalid characters" in message

    def test_handle_parse_error(self):
        """Test handling ParseError."""
        handler = ErrorHandler()
        error = ParseError("Cannot parse field")
        message = handler.handle_error(error)

        assert "✗ Parse error" in message
        assert "Cannot parse field" in message

    def test_handle_generic_cronpal_error(self):
        """Test handling generic CronPalError."""
        handler = ErrorHandler()
        error = CronPalError("Generic error")
        message = handler.handle_error(error)

        assert "✗ Error" in message
        assert "Generic error" in message

    def test_handle_unexpected_error(self):
        """Test handling unexpected errors."""
        handler = ErrorHandler(verbose=True)
        error = ValueError("Unexpected issue")
        message = handler.handle_error(error, "test")

        assert "✗ Unexpected error" in message
        assert "Unexpected issue" in message
        assert "Error type: ValueError" in message

    def test_error_count(self):
        """Test error counting."""
        handler = ErrorHandler()
        assert handler.error_count == 0

        handler.handle_error(ValidationError("Test"))
        assert handler.error_count == 1

        handler.handle_error(ParseError("Test"))
        assert handler.error_count == 2

        handler.reset()
        assert handler.error_count == 0

    def test_print_error_to_stderr(self):
        """Test printing error to stderr."""
        handler = ErrorHandler()
        error = InvalidCronExpression("Test error")

        output = StringIO()
        handler.print_error(error, file=output)

        result = output.getvalue()
        assert "✗ Invalid cron expression" in result
        assert "Test error" in result

    def test_print_error_with_expression(self):
        """Test printing error with expression."""
        handler = ErrorHandler(verbose=True)
        error = ValidationError("Bad format")

        output = StringIO()
        handler.print_error(error, expression="* * *", file=output)

        result = output.getvalue()
        assert "✗ Validation failed" in result
        assert "Expression: '* * *'" in result


class TestSuggestFix:
    """Tests for suggest_fix function."""

    def test_suggest_for_too_few_fields(self):
        """Test suggestion for too few fields."""
        error = InvalidCronExpression("Invalid number of fields")
        suggestion = suggest_fix(error, "0 0 *")

        assert suggestion is not None
        assert "Add missing fields" in suggestion
        assert "0 0 * * *" in suggestion

    def test_suggest_for_too_many_fields(self):
        """Test suggestion for too many fields."""
        error = InvalidCronExpression("Invalid number of fields")
        suggestion = suggest_fix(error, "0 0 * * * * *")

        assert suggestion is not None
        assert "Remove extra fields" in suggestion
        assert "5 fields" in suggestion

    def test_suggest_for_invalid_character(self):
        """Test suggestion for invalid characters."""
        error = ValidationError("Invalid character: @")
        suggestion = suggest_fix(error, "0 0 @ * *")

        assert suggestion is not None
        assert "Use only numbers" in suggestion

    def test_suggest_for_empty(self):
        """Test suggestion for empty expression."""
        error = InvalidCronExpression("Empty expression")
        suggestion = suggest_fix(error, "")

        assert suggestion is not None
        assert "Provide a cron expression" in suggestion
        assert "0 0 * * *" in suggestion

    def test_suggest_for_unknown_special(self):
        """Test suggestion for unknown special string."""
        error = InvalidCronExpression("Unknown special string")
        suggestion = suggest_fix(error, "@invalid")

        assert suggestion is not None
        assert "@yearly" in suggestion
        assert "@daily" in suggestion
        assert "@reboot" in suggestion

    def test_no_suggestion(self):
        """Test when no suggestion is available."""
        error = ParseError("Complex parsing issue")
        suggestion = suggest_fix(error, "complex")

        assert suggestion is None