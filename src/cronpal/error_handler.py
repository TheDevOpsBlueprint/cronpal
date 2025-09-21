"""Error handling utilities for CronPal."""

import sys
from typing import Optional

from cronpal.exceptions import (
    CronPalError,
    FieldError,
    InvalidCronExpression,
    ParseError,
    ValidationError,
)


class ErrorHandler:
    """Centralized error handling for CronPal."""

    def __init__(self, verbose: bool = False):
        """
        Initialize error handler.

        Args:
            verbose: Whether to show detailed error messages.
        """
        self.verbose = verbose
        self.error_count = 0

    def handle_error(self, error: Exception, expression: Optional[str] = None) -> str:
        """
        Handle an error and return formatted message.

        Args:
            error: The exception to handle.
            expression: Optional cron expression being processed.

        Returns:
            Formatted error message.
        """
        self.error_count += 1

        if isinstance(error, InvalidCronExpression):
            return self._handle_invalid_expression(error, expression)
        elif isinstance(error, FieldError):
            return self._handle_field_error(error, expression)
        elif isinstance(error, ValidationError):
            return self._handle_validation_error(error, expression)
        elif isinstance(error, ParseError):
            return self._handle_parse_error(error, expression)
        elif isinstance(error, CronPalError):
            return self._handle_generic_cronpal_error(error, expression)
        else:
            return self._handle_unexpected_error(error, expression)

    def _handle_invalid_expression(
            self,
            error: InvalidCronExpression,
            expression: Optional[str]
    ) -> str:
        """Handle InvalidCronExpression."""
        message = f"✗ Invalid cron expression: {error}"

        if self.verbose and expression:
            message += f"\n  Expression: '{expression}'"
            message += "\n  Expected format: <minute> <hour> <day> <month> <weekday>"

        return message

    def _handle_field_error(
            self,
            error: FieldError,
            expression: Optional[str]
    ) -> str:
        """Handle FieldError."""
        message = f"✗ Field error in {error.field_name}: {str(error)}"

        if self.verbose and expression:
            message += f"\n  Expression: '{expression}'"

        return message

    def _handle_validation_error(
            self,
            error: ValidationError,
            expression: Optional[str]
    ) -> str:
        """Handle ValidationError."""
        message = f"✗ Validation failed: {error}"

        if self.verbose and expression:
            message += f"\n  Expression: '{expression}'"

        return message

    def _handle_parse_error(
            self,
            error: ParseError,
            expression: Optional[str]
    ) -> str:
        """Handle ParseError."""
        message = f"✗ Parse error: {error}"

        if self.verbose and expression:
            message += f"\n  Expression: '{expression}'"

        return message

    def _handle_generic_cronpal_error(
            self,
            error: CronPalError,
            expression: Optional[str]
    ) -> str:
        """Handle generic CronPalError."""
        message = f"✗ Error: {error}"

        if self.verbose and expression:
            message += f"\n  Expression: '{expression}'"

        return message

    def _handle_unexpected_error(
            self,
            error: Exception,
            expression: Optional[str]
    ) -> str:
        """Handle unexpected errors."""
        message = f"✗ Unexpected error: {error}"

        if self.verbose:
            message += f"\n  Error type: {type(error).__name__}"
            if expression:
                message += f"\n  Expression: '{expression}'"

        return message

    def print_error(
            self,
            error: Exception,
            expression: Optional[str] = None,
            file=None
    ) -> None:
        """
        Print error message to specified file.

        Args:
            error: The exception to handle.
            expression: Optional cron expression being processed.
            file: File to write to (default: stderr).
        """
        if file is None:
            file = sys.stderr

        message = self.handle_error(error, expression)
        print(message, file=file)

    def reset(self) -> None:
        """Reset error counter."""
        self.error_count = 0


def suggest_fix(error: Exception, expression: str) -> Optional[str]:
    """
    Suggest a fix for common errors.

    Args:
        error: The error that occurred.
        expression: The cron expression that caused the error.

    Returns:
        Suggestion string or None.
    """
    error_str = str(error).lower()

    if "invalid number of fields" in error_str:
        fields = expression.split()
        if len(fields) < 5:
            return "Add missing fields. Example: '0 0 * * *' for daily at midnight"
        elif len(fields) > 5:
            return "Remove extra fields. Standard cron uses 5 fields"

    elif "invalid character" in error_str:
        return "Use only numbers, wildcards (*), ranges (-), lists (,), and steps (/)"

    elif "empty" in error_str:
        return "Provide a cron expression. Example: '0 0 * * *' for daily at midnight"

    elif "unknown special string" in error_str:
        return "Valid special strings: @yearly, @monthly, @weekly, @daily, @hourly, @reboot"

    return None