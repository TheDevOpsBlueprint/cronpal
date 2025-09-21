"""Field parsing logic for cron expressions."""

from typing import List, Set

from cronpal.constants import DAY_NAMES, MONTH_NAMES, WILDCARD
from cronpal.exceptions import FieldError, ParseError
from cronpal.models import CronField, FieldRange, FieldType, FIELD_RANGES


class FieldParser:
    """Parser for individual cron fields."""

    def parse_minute(self, field_value: str) -> CronField:
        """
        Parse the minute field of a cron expression.

        Args:
            field_value: The minute field string (e.g., "0", "*/5", "0-30").

        Returns:
            CronField object with parsed values.

        Raises:
            FieldError: If the field value is invalid.
        """
        field_type = FieldType.MINUTE
        field_range = FIELD_RANGES[field_type]

        try:
            parsed_values = self._parse_field(
                field_value,
                field_range,
                "minute"
            )

            field = CronField(
                raw_value=field_value,
                field_type=field_type,
                field_range=field_range
            )
            field.parsed_values = parsed_values
            return field

        except (ParseError, ValueError) as e:
            raise FieldError("minute", str(e))

    def parse_hour(self, field_value: str) -> CronField:
        """
        Parse the hour field of a cron expression.

        Args:
            field_value: The hour field string (e.g., "0", "*/2", "9-17").

        Returns:
            CronField object with parsed values.

        Raises:
            FieldError: If the field value is invalid.
        """
        field_type = FieldType.HOUR
        field_range = FIELD_RANGES[field_type]

        try:
            parsed_values = self._parse_field(
                field_value,
                field_range,
                "hour"
            )

            field = CronField(
                raw_value=field_value,
                field_type=field_type,
                field_range=field_range
            )
            field.parsed_values = parsed_values
            return field

        except (ParseError, ValueError) as e:
            raise FieldError("hour", str(e))

    def parse_day_of_month(self, field_value: str) -> CronField:
        """
        Parse the day of month field of a cron expression.

        Args:
            field_value: The day field string (e.g., "1", "*/2", "1-15").

        Returns:
            CronField object with parsed values.

        Raises:
            FieldError: If the field value is invalid.
        """
        field_type = FieldType.DAY_OF_MONTH
        field_range = FIELD_RANGES[field_type]

        try:
            parsed_values = self._parse_field(
                field_value,
                field_range,
                "day of month"
            )

            field = CronField(
                raw_value=field_value,
                field_type=field_type,
                field_range=field_range
            )
            field.parsed_values = parsed_values
            return field

        except (ParseError, ValueError) as e:
            raise FieldError("day of month", str(e))

    def parse_month(self, field_value: str) -> CronField:
        """
        Parse the month field of a cron expression.

        Args:
            field_value: The month field string (e.g., "1", "JAN", "JAN-MAR").

        Returns:
            CronField object with parsed values.

        Raises:
            FieldError: If the field value is invalid.
        """
        field_type = FieldType.MONTH
        field_range = FIELD_RANGES[field_type]

        try:
            # Replace month names with numbers
            normalized = self._normalize_month_names(field_value)

            parsed_values = self._parse_field(
                normalized,
                field_range,
                "month"
            )

            field = CronField(
                raw_value=field_value,
                field_type=field_type,
                field_range=field_range
            )
            field.parsed_values = parsed_values
            return field

        except (ParseError, ValueError) as e:
            raise FieldError("month", str(e))

    def parse_day_of_week(self, field_value: str) -> CronField:
        """
        Parse the day of week field of a cron expression.

        Args:
            field_value: The day field string (e.g., "0", "MON", "MON-FRI").

        Returns:
            CronField object with parsed values.

        Raises:
            FieldError: If the field value is invalid.
        """
        field_type = FieldType.DAY_OF_WEEK
        field_range = FIELD_RANGES[field_type]

        try:
            # Replace day names with numbers
            normalized = self._normalize_day_names(field_value)

            parsed_values = self._parse_field(
                normalized,
                field_range,
                "day of week"
            )

            # Handle Sunday as both 0 and 7
            if 7 in parsed_values:
                parsed_values.add(0)
                parsed_values.remove(7)

            field = CronField(
                raw_value=field_value,
                field_type=field_type,
                field_range=field_range
            )
            field.parsed_values = parsed_values
            return field

        except (ParseError, ValueError) as e:
            raise FieldError("day of week", str(e))

    def _normalize_month_names(self, field_value: str) -> str:
        """
        Replace month names with their numeric values.

        Args:
            field_value: The field value possibly containing month names.

        Returns:
            Field value with month names replaced by numbers.
        """
        normalized = field_value.upper()

        # Replace month names with numbers
        for name, number in MONTH_NAMES.items():
            normalized = normalized.replace(name, str(number))

        return normalized

    def _normalize_day_names(self, field_value: str) -> str:
        """
        Replace day names with their numeric values.

        Args:
            field_value: The field value possibly containing day names.

        Returns:
            Field value with day names replaced by numbers.
        """
        normalized = field_value.upper()

        # Replace day names with numbers
        for name, number in DAY_NAMES.items():
            normalized = normalized.replace(name, str(number))

        return normalized

    def _parse_field(
        self,
        field_value: str,
        field_range: FieldRange,
        field_name: str
    ) -> Set[int]:
        """
        Parse a field value into a set of integers.

        Args:
            field_value: The field value to parse.
            field_range: The valid range for this field.
            field_name: The name of the field for error messages.

        Returns:
            Set of valid integer values.

        Raises:
            ParseError: If parsing fails.
        """
        if not field_value:
            raise ParseError(f"Empty {field_name} field")

        # Handle wildcard
        if field_value == WILDCARD:
            return set(range(field_range.min_value, field_range.max_value + 1))

        values = set()

        # Split by comma for lists
        for part in field_value.split(","):
            part = part.strip()

            # Skip empty parts
            if not part:
                continue

            # Handle wildcards in lists (e.g., "*,*")
            if part == WILDCARD:
                return set(range(field_range.min_value, field_range.max_value + 1))

            if "/" in part:
                # Handle step values (e.g., "*/5" or "0-30/5")
                values.update(self._parse_step(part, field_range, field_name))
            elif "-" in part and not self._is_negative_number(part):
                # Handle ranges (e.g., "0-30")
                values.update(self._parse_range(part, field_range, field_name))
            else:
                # Handle single values (including negative numbers)
                value = self._parse_single(part, field_range, field_name)
                values.add(value)

        return values

    def _is_negative_number(self, value_str: str) -> bool:
        """
        Check if a string represents a negative number.

        Args:
            value_str: The string to check.

        Returns:
            True if the string is a negative number like "-1".
        """
        # Check if it starts with minus and the rest is a number
        if value_str.startswith("-") and len(value_str) > 1:
            try:
                int(value_str)
                return True
            except ValueError:
                return False
        return False

    def _parse_single(
        self,
        value_str: str,
        field_range: FieldRange,
        field_name: str
    ) -> int:
        """
        Parse a single numeric value.

        Args:
            value_str: The value string to parse.
            field_range: The valid range for this field.
            field_name: The name of the field for error messages.

        Returns:
            The parsed integer value.

        Raises:
            ParseError: If the value is invalid.
        """
        try:
            value = int(value_str)
        except ValueError:
            raise ParseError(
                f"Invalid {field_name} value: '{value_str}' is not a number"
            )

        if value < field_range.min_value or value > field_range.max_value:
            raise ParseError(
                f"{field_name} value {value} out of range "
                f"[{field_range.min_value}-{field_range.max_value}]"
            )

        return value

    def _parse_range(
        self,
        range_str: str,
        field_range: FieldRange,
        field_name: str
    ) -> Set[int]:
        """
        Parse a range expression (e.g., "0-30").

        Args:
            range_str: The range string to parse.
            field_range: The valid range for this field.
            field_name: The name of the field for error messages.

        Returns:
            Set of values in the range.

        Raises:
            ParseError: If the range is invalid.
        """
        parts = range_str.split("-")

        if len(parts) != 2:
            raise ParseError(
                f"Invalid range in {field_name}: '{range_str}'"
            )

        start = self._parse_single(parts[0], field_range, field_name)
        end = self._parse_single(parts[1], field_range, field_name)

        if start > end:
            raise ParseError(
                f"Invalid range in {field_name}: start ({start}) > end ({end})"
            )

        return set(range(start, end + 1))

    def _parse_step(
        self,
        step_str: str,
        field_range: FieldRange,
        field_name: str
    ) -> Set[int]:
        """
        Parse a step expression (e.g., "*/5" or "0-30/5").

        Args:
            step_str: The step string to parse.
            field_range: The valid range for this field.
            field_name: The name of the field for error messages.

        Returns:
            Set of values according to the step.

        Raises:
            ParseError: If the step is invalid.
        """
        parts = step_str.split("/")

        if len(parts) != 2:
            raise ParseError(
                f"Invalid step in {field_name}: '{step_str}'"
            )

        # Parse the step value
        try:
            step = int(parts[1])
        except ValueError:
            raise ParseError(
                f"Invalid step value in {field_name}: '{parts[1]}'"
            )

        if step <= 0:
            raise ParseError(
                f"Step value must be positive in {field_name}: {step}"
            )

        # Parse the base range
        base = parts[0]
        if base == WILDCARD:
            start = field_range.min_value
            end = field_range.max_value
        elif "-" in base:
            range_values = self._parse_range(base, field_range, field_name)
            start = min(range_values)
            end = max(range_values)
        else:
            start = self._parse_single(base, field_range, field_name)
            end = field_range.max_value

        # Generate values with step
        values = set()
        current = start
        while current <= end:
            values.add(current)
            current += step

        return values