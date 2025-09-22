"""Special string parser for cron expressions."""

from cronpal.constants import SPECIAL_STRINGS
from cronpal.exceptions import InvalidCronExpression
from cronpal.field_parser import FieldParser
from cronpal.models import CronExpression


class SpecialStringParser:
    """Parser for special cron strings like @yearly, @daily, etc."""

    def __init__(self):
        """Initialize the special string parser."""
        self.field_parser = FieldParser()

    def is_special_string(self, expression: str) -> bool:
        """
        Check if an expression is a special string.

        Args:
            expression: The expression to check.

        Returns:
            True if it's a special string, False otherwise.
        """
        return expression.strip().lower() in [s.lower() for s in SPECIAL_STRINGS.keys()]

    def parse(self, special_string: str) -> CronExpression:
        """
        Parse a special string into a CronExpression.

        Args:
            special_string: The special string to parse (e.g., "@daily").

        Returns:
            A CronExpression object with parsed fields.

        Raises:
            InvalidCronExpression: If the string is not recognized.
        """
        special_string = special_string.strip()

        # Check if it's a valid special string
        if special_string not in SPECIAL_STRINGS:
            # Try case-insensitive match
            special_lower = special_string.lower()
            matching_key = None
            for key in SPECIAL_STRINGS.keys():
                if key.lower() == special_lower:
                    matching_key = key
                    break

            if not matching_key:
                available = ", ".join(sorted(SPECIAL_STRINGS.keys()))
                raise InvalidCronExpression(
                    f"Unknown special string: '{special_string}'. "
                    f"Available: {available}"
                )
            special_string = matching_key

        # Get the expanded expression
        expanded = SPECIAL_STRINGS[special_string]

        # Create the CronExpression with the original special string
        cron_expr = CronExpression(special_string)

        # Handle @reboot specially - it doesn't expand to standard fields
        if special_string == "@reboot":
            # @reboot is a special case that doesn't have time fields
            return cron_expr

        # Parse the expanded expression fields
        fields = expanded.split()
        if len(fields) != 5:
            raise InvalidCronExpression(
                f"Invalid expansion for {special_string}: {expanded}"
            )

        # Parse each field using the field parser
        cron_expr.minute = self.field_parser.parse_minute(fields[0])
        cron_expr.hour = self.field_parser.parse_hour(fields[1])
        cron_expr.day_of_month = self.field_parser.parse_day_of_month(fields[2])
        cron_expr.month = self.field_parser.parse_month(fields[3])
        cron_expr.day_of_week = self.field_parser.parse_day_of_week(fields[4])

        return cron_expr

    def get_description(self, special_string: str) -> str:
        """
        Get a human-readable description of a special string.

        Args:
            special_string: The special string to describe.

        Returns:
            A human-readable description.
        """
        descriptions = {
            "@yearly": "Run once a year at midnight on January 1st",
            "@annually": "Run once a year at midnight on January 1st",
            "@monthly": "Run once a month at midnight on the 1st",
            "@weekly": "Run once a week at midnight on Sunday",
            "@daily": "Run once a day at midnight",
            "@midnight": "Run once a day at midnight",
            "@hourly": "Run once an hour at the beginning of the hour",
            "@reboot": "Run at system startup"
        }

        # Normalize the string
        special_string = special_string.strip().lower()
        for key, desc in descriptions.items():
            if key.lower() == special_string:
                return desc

        return f"Unknown special string: {special_string}"