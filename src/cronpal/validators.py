"""Validation functions for cron expressions."""

from typing import Dict, List, Optional

from cronpal.constants import SPECIAL_STRINGS
from cronpal.exceptions import InvalidCronExpression, ValidationError


def validate_expression_format(expression: str) -> List[str]:
    """
    Validate the basic format of a cron expression.

    Args:
        expression: The cron expression string to validate.

    Returns:
        List of field strings if valid.

    Raises:
        InvalidCronExpression: If the expression format is invalid.
    """
    if not expression:
        raise InvalidCronExpression("Empty cron expression provided")

    expression = expression.strip()

    if not expression:
        raise InvalidCronExpression("Empty cron expression after trimming whitespace")

    # Check for special strings
    if expression.startswith("@"):
        if expression in SPECIAL_STRINGS:
            # Return the expanded expression
            if expression == "@reboot":
                # Special case - cannot be expanded
                return [expression]
            return SPECIAL_STRINGS[expression].split()
        else:
            available = ", ".join(sorted(SPECIAL_STRINGS.keys()))
            raise InvalidCronExpression(
                f"Unknown special string: '{expression}'. Available: {available}"
            )

    # Split the expression into fields
    fields = expression.split()

    # Standard cron has 5 fields (minute hour day month weekday)
    if len(fields) != 5:
        raise InvalidCronExpression(
            f"Invalid number of fields: expected 5, got {len(fields)}. "
            f"Format should be: <minute> <hour> <day> <month> <weekday>"
        )

    return fields


def validate_field_characters(field: str, field_name: str) -> None:
    """
    Validate that a field contains only valid characters.

    Args:
        field: The field value to validate.
        field_name: The name of the field for error messages.

    Raises:
        ValidationError: If invalid characters are found.
    """
    valid_chars = set("0123456789*-/,")

    # For month and day of week, also allow letters
    if field_name in ["month", "day_of_week"]:
        valid_chars.update(set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))

    field_upper = field.upper()
    invalid_chars = set(field_upper) - valid_chars

    if invalid_chars:
        char_list = ", ".join(f"'{c}'" for c in sorted(invalid_chars))
        raise ValidationError(
            f"Invalid characters in {field_name} field: {char_list}. "
            f"Field value was: '{field}'"
        )


def get_field_info() -> Dict[str, Dict[str, any]]:
    """
    Get information about cron fields.

    Returns:
        Dictionary with field information.
    """
    return {
        "minute": {"range": "0-59", "position": 1},
        "hour": {"range": "0-23", "position": 2},
        "day_of_month": {"range": "1-31", "position": 3},
        "month": {"range": "1-12", "position": 4},
        "day_of_week": {"range": "0-7", "position": 5},
    }


def validate_expression(expression: str) -> bool:
    """
    Perform basic validation of a cron expression.

    Args:
        expression: The cron expression to validate.

    Returns:
        True if valid.

    Raises:
        InvalidCronExpression: If validation fails.
        ValidationError: If field validation fails.
    """
    fields = validate_expression_format(expression)

    if len(fields) == 1 and fields[0] == "@reboot":
        # Special case for @reboot
        return True

    field_names = ["minute", "hour", "day_of_month", "month", "day_of_week"]
    field_info = get_field_info()

    for field, name in zip(fields, field_names):
        try:
            validate_field_characters(field, name)
        except ValidationError as e:
            # Add field position and range info
            info = field_info[name]
            raise ValidationError(
                f"{e} (Position {info['position']}, Valid range: {info['range']})"
            )

    return True