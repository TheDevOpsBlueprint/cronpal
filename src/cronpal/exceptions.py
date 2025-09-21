"""Custom exceptions for CronPal."""


class CronPalError(Exception):
    """Base exception for all CronPal errors."""

    pass


class InvalidCronExpression(CronPalError):
    """Raised when a cron expression is invalid."""

    pass


class ValidationError(CronPalError):
    """Raised when validation fails."""

    pass


class ParseError(CronPalError):
    """Raised when parsing fails."""

    pass


class FieldError(CronPalError):
    """Raised when a field value is invalid."""

    def __init__(self, field_name: str, message: str):
        """Initialize with field name and message."""
        self.field_name = field_name
        super().__init__(f"{field_name}: {message}")