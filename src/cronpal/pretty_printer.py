"""Pretty printer for cron expressions."""

from typing import List, Optional, Set

from cronpal.models import CronExpression, CronField, FieldType


class PrettyPrinter:
    """Pretty printer for cron expressions."""

    def __init__(self, expression: CronExpression):
        """
        Initialize the pretty printer.

        Args:
            expression: The CronExpression to pretty print.
        """
        self.expression = expression

    def print_table(self) -> str:
        """
        Generate a formatted table of the cron expression.

        Returns:
            A string containing the formatted table.
        """
        lines = []

        # Header
        lines.append("┌" + "─" * 78 + "┐")
        lines.append(f"│ {'Cron Expression Analysis':^76} │")
        lines.append("├" + "─" * 78 + "┤")
        lines.append(f"│ Expression: {self.expression.raw_expression:<63} │")
        lines.append("├" + "─" * 17 + "┬" + "─" * 15 + "┬" + "─" * 44 + "┤")
        lines.append("│ Field           │ Value         │ Description                                │")
        lines.append("├" + "─" * 17 + "┼" + "─" * 15 + "┼" + "─" * 44 + "┤")

        # Fields
        if self.expression.minute:
            lines.append(self._format_field_row("Minute", self.expression.minute))

        if self.expression.hour:
            lines.append(self._format_field_row("Hour", self.expression.hour))

        if self.expression.day_of_month:
            lines.append(self._format_field_row("Day of Month", self.expression.day_of_month))

        if self.expression.month:
            lines.append(self._format_field_row("Month", self.expression.month))

        if self.expression.day_of_week:
            lines.append(self._format_field_row("Day of Week", self.expression.day_of_week))

        # Footer
        lines.append("└" + "─" * 17 + "┴" + "─" * 15 + "┴" + "─" * 44 + "┘")

        return "\n".join(lines)

    def print_simple(self) -> str:
        """
        Generate a simple formatted output of the cron expression.

        Returns:
            A string containing the simple formatted output.
        """
        lines = []
        lines.append(f"Cron Expression: {self.expression.raw_expression}")
        lines.append("-" * 50)

        if self.expression.minute:
            lines.append(f"Minute:       {self.expression.minute.raw_value:10} {self._describe_field(self.expression.minute)}")

        if self.expression.hour:
            lines.append(f"Hour:         {self.expression.hour.raw_value:10} {self._describe_field(self.expression.hour)}")

        if self.expression.day_of_month:
            lines.append(f"Day of Month: {self.expression.day_of_month.raw_value:10} {self._describe_field(self.expression.day_of_month)}")

        if self.expression.month:
            lines.append(f"Month:        {self.expression.month.raw_value:10} {self._describe_field(self.expression.month)}")

        if self.expression.day_of_week:
            lines.append(f"Day of Week:  {self.expression.day_of_week.raw_value:10} {self._describe_field(self.expression.day_of_week)}")

        return "\n".join(lines)

    def print_detailed(self) -> str:
        """
        Generate a detailed output with parsed values.

        Returns:
            A string containing the detailed output.
        """
        lines = []
        lines.append("═" * 80)
        lines.append(f" CRON EXPRESSION: {self.expression.raw_expression}")
        lines.append("═" * 80)

        if self.expression.minute:
            lines.extend(self._format_detailed_field("MINUTE", self.expression.minute))

        if self.expression.hour:
            lines.extend(self._format_detailed_field("HOUR", self.expression.hour))

        if self.expression.day_of_month:
            lines.extend(self._format_detailed_field("DAY OF MONTH", self.expression.day_of_month))

        if self.expression.month:
            lines.extend(self._format_detailed_field("MONTH", self.expression.month))

        if self.expression.day_of_week:
            lines.extend(self._format_detailed_field("DAY OF WEEK", self.expression.day_of_week))

        lines.append("═" * 80)

        return "\n".join(lines)

    def get_summary(self) -> str:
        """
        Generate a human-readable summary of when the cron runs.

        Returns:
            A string with a human-readable description.
        """
        parts = []

        # Check for common patterns
        if self._is_every_minute():
            return "Runs every minute"

        if self._is_hourly():
            minute = list(self.expression.minute.parsed_values)[0] if self.expression.minute else 0
            return f"Runs every hour at minute {minute:02d}"

        if self._is_daily():
            hour = list(self.expression.hour.parsed_values)[0] if self.expression.hour else 0
            minute = list(self.expression.minute.parsed_values)[0] if self.expression.minute else 0
            return f"Runs daily at {hour:02d}:{minute:02d}"

        if self._is_weekly():
            day = self._get_single_weekday_name()
            hour = list(self.expression.hour.parsed_values)[0] if self.expression.hour else 0
            minute = list(self.expression.minute.parsed_values)[0] if self.expression.minute else 0
            return f"Runs every {day} at {hour:02d}:{minute:02d}"

        if self._is_monthly():
            day = list(self.expression.day_of_month.parsed_values)[0] if self.expression.day_of_month else 1
            hour = list(self.expression.hour.parsed_values)[0] if self.expression.hour else 0
            minute = list(self.expression.minute.parsed_values)[0] if self.expression.minute else 0
            return f"Runs on day {day} of every month at {hour:02d}:{minute:02d}"

        if self._is_yearly():
            month = list(self.expression.month.parsed_values)[0] if self.expression.month else 1
            day = list(self.expression.day_of_month.parsed_values)[0] if self.expression.day_of_month else 1
            hour = list(self.expression.hour.parsed_values)[0] if self.expression.hour else 0
            minute = list(self.expression.minute.parsed_values)[0] if self.expression.minute else 0
            month_name = self._get_month_name(month)
            return f"Runs on {month_name} {day} at {hour:02d}:{minute:02d}"

        # Complex expression - build description from parts
        time_part = self._describe_time()
        date_part = self._describe_date()

        if time_part and date_part:
            return f"Runs {time_part} {date_part}"
        elif time_part:
            return f"Runs {time_part}"
        elif date_part:
            return f"Runs {date_part}"
        else:
            return "Complex schedule"

    def _format_field_row(self, name: str, field: CronField) -> str:
        """Format a single field row for the table."""
        description = self._describe_field(field)
        # Truncate description if too long
        if len(description) > 42:
            description = description[:39] + "..."

        return f"│ {name:<15} │ {field.raw_value:<13} │ {description:<42} │"

    def _format_detailed_field(self, name: str, field: CronField) -> List[str]:
        """Format detailed field information."""
        lines = []
        lines.append("")
        lines.append(f"▸ {name}")
        lines.append("  " + "─" * 76)
        lines.append(f"  Raw Value:    {field.raw_value}")
        lines.append(f"  Range:        {field.field_range.min_value}-{field.field_range.max_value}")
        lines.append(f"  Description:  {self._describe_field(field)}")

        if field.parsed_values:
            values_str = self._format_value_list(field.parsed_values, field.field_type)
            lines.append(f"  Values:       {values_str}")

        return lines

    def _format_value_list(self, values: Set[int], field_type: FieldType) -> str:
        """Format a list of values for display."""
        sorted_values = sorted(values)

        if len(sorted_values) > 20:
            # Show first 10 and last 5 with ellipsis
            first_part = sorted_values[:10]
            last_part = sorted_values[-5:]

            first_str = ", ".join(str(v) for v in first_part)
            last_str = ", ".join(str(v) for v in last_part)
            return f"{first_str} ... {last_str} ({len(sorted_values)} values)"
        else:
            if field_type == FieldType.MONTH:
                return ", ".join(f"{v} ({self._get_month_name(v)})" for v in sorted_values)
            elif field_type == FieldType.DAY_OF_WEEK:
                return ", ".join(f"{v} ({self._get_weekday_name(v)})" for v in sorted_values)
            else:
                return ", ".join(str(v) for v in sorted_values)

    def _describe_field(self, field: CronField) -> str:
        """Generate a human-readable description of a field."""
        if field.is_wildcard():
            return f"Every {self._get_field_name(field.field_type)}"

        if not field.parsed_values:
            return field.raw_value

        values = field.parsed_values

        # Check for special patterns
        # Check if it's an actual step pattern from the raw value
        if "/" in field.raw_value:
            step = self._get_step_value(values)
            if "*/" in field.raw_value:
                return f"Every {step} {self._get_field_name_plural(field.field_type)}"
            else:
                return f"Every {step} {self._get_field_name_plural(field.field_type)} from {min(values)}"

        if self._is_range(values) and "-" in field.raw_value and "/" not in field.raw_value:
            min_val = min(values)
            max_val = max(values)
            return f"From {min_val} to {max_val}"

        if len(values) == 1:
            val = list(values)[0]
            if field.field_type == FieldType.MONTH:
                return self._get_month_name(val)
            elif field.field_type == FieldType.DAY_OF_WEEK:
                return self._get_weekday_name(val)
            else:
                return f"At {self._get_field_name(field.field_type)} {val}"

        if len(values) <= 5:
            if field.field_type == FieldType.MONTH:
                names = [self._get_month_name(v) for v in sorted(values)]
                return ", ".join(names)
            elif field.field_type == FieldType.DAY_OF_WEEK:
                names = [self._get_weekday_name(v) for v in sorted(values)]
                return ", ".join(names)
            else:
                return f"At {self._get_field_name_plural(field.field_type)} " + ", ".join(str(v) for v in sorted(values))

        return f"{len(values)} selected {self._get_field_name_plural(field.field_type)}"

    def _describe_time(self) -> str:
        """Describe the time portion of the cron expression."""
        if not self.expression.minute or not self.expression.hour:
            return ""

        minute_vals = self.expression.minute.parsed_values
        hour_vals = self.expression.hour.parsed_values

        if len(minute_vals) == 1 and len(hour_vals) == 1:
            minute = list(minute_vals)[0]
            hour = list(hour_vals)[0]
            return f"at {hour:02d}:{minute:02d}"

        if len(minute_vals) == 1:
            minute = list(minute_vals)[0]
            return f"at minute {minute:02d} of selected hours"

        if len(hour_vals) == 1:
            hour = list(hour_vals)[0]
            return f"at selected minutes of hour {hour}"

        return "at selected times"

    def _describe_date(self) -> str:
        """Describe the date portion of the cron expression."""
        parts = []

        if self.expression.day_of_month and not self.expression.day_of_month.is_wildcard():
            days = self.expression.day_of_month.parsed_values
            if len(days) == 1:
                parts.append(f"on day {list(days)[0]}")
            else:
                parts.append(f"on days {self._format_short_list(days)}")

        if self.expression.month and not self.expression.month.is_wildcard():
            months = self.expression.month.parsed_values
            if len(months) == 1:
                parts.append(f"in {self._get_month_name(list(months)[0])}")
            else:
                month_names = [self._get_month_name(m) for m in sorted(months)[:3]]
                if len(months) > 3:
                    parts.append(f"in {', '.join(month_names)}...")
                else:
                    parts.append(f"in {', '.join(month_names)}")

        if self.expression.day_of_week and not self.expression.day_of_week.is_wildcard():
            weekdays = self.expression.day_of_week.parsed_values
            if len(weekdays) == 1:
                parts.append(f"on {self._get_weekday_name(list(weekdays)[0])}")
            else:
                day_names = [self._get_weekday_name(d) for d in sorted(weekdays)[:3]]
                if len(weekdays) > 3:
                    parts.append(f"on {', '.join(day_names)}...")
                else:
                    parts.append(f"on {', '.join(day_names)}")

        return " ".join(parts)

    def _format_short_list(self, values: Set[int]) -> str:
        """Format a short list of values."""
        sorted_vals = sorted(values)
        if len(sorted_vals) <= 5:
            return ", ".join(str(v) for v in sorted_vals)
        else:
            return f"{sorted_vals[0]}, {sorted_vals[1]}, ... {sorted_vals[-1]}"

    def _is_range(self, values: Set[int]) -> bool:
        """Check if values form a continuous range."""
        if len(values) < 2:
            return False
        sorted_vals = sorted(values)
        return sorted_vals == list(range(sorted_vals[0], sorted_vals[-1] + 1))

    def _is_step(self, values: Set[int], min_val: int, max_val: int) -> bool:
        """Check if values form a step pattern."""
        if len(values) < 2:
            return False
        sorted_vals = sorted(values)
        if len(sorted_vals) < 2:
            return False

        step = sorted_vals[1] - sorted_vals[0]
        if step <= 0:
            return False

        for i in range(1, len(sorted_vals)):
            if sorted_vals[i] - sorted_vals[i-1] != step:
                return False

        return True

    def _get_step_value(self, values: Set[int]) -> int:
        """Get the step value from a set of values."""
        sorted_vals = sorted(values)
        if len(sorted_vals) >= 2:
            return sorted_vals[1] - sorted_vals[0]
        return 1

    def _is_every_minute(self) -> bool:
        """Check if expression runs every minute."""
        return (self.expression.minute and self.expression.minute.is_wildcard() and
                self.expression.hour and self.expression.hour.is_wildcard() and
                self.expression.day_of_month and self.expression.day_of_month.is_wildcard() and
                self.expression.month and self.expression.month.is_wildcard() and
                self.expression.day_of_week and self.expression.day_of_week.is_wildcard())

    def _is_hourly(self) -> bool:
        """Check if expression runs hourly."""
        return (self.expression.minute and len(self.expression.minute.parsed_values) == 1 and
                self.expression.hour and self.expression.hour.is_wildcard() and
                self.expression.day_of_month and self.expression.day_of_month.is_wildcard() and
                self.expression.month and self.expression.month.is_wildcard() and
                self.expression.day_of_week and self.expression.day_of_week.is_wildcard())

    def _is_daily(self) -> bool:
        """Check if expression runs daily."""
        return (self.expression.minute and len(self.expression.minute.parsed_values) == 1 and
                self.expression.hour and len(self.expression.hour.parsed_values) == 1 and
                self.expression.day_of_month and self.expression.day_of_month.is_wildcard() and
                self.expression.month and self.expression.month.is_wildcard() and
                self.expression.day_of_week and self.expression.day_of_week.is_wildcard())

    def _is_weekly(self) -> bool:
        """Check if expression runs weekly."""
        return (self.expression.minute and len(self.expression.minute.parsed_values) == 1 and
                self.expression.hour and len(self.expression.hour.parsed_values) == 1 and
                self.expression.day_of_month and self.expression.day_of_month.is_wildcard() and
                self.expression.month and self.expression.month.is_wildcard() and
                self.expression.day_of_week and len(self.expression.day_of_week.parsed_values) == 1)

    def _is_monthly(self) -> bool:
        """Check if expression runs monthly."""
        return (self.expression.minute and len(self.expression.minute.parsed_values) == 1 and
                self.expression.hour and len(self.expression.hour.parsed_values) == 1 and
                self.expression.day_of_month and len(self.expression.day_of_month.parsed_values) == 1 and
                self.expression.month and self.expression.month.is_wildcard() and
                self.expression.day_of_week and self.expression.day_of_week.is_wildcard())

    def _is_yearly(self) -> bool:
        """Check if expression runs yearly."""
        return (self.expression.minute and len(self.expression.minute.parsed_values) == 1 and
                self.expression.hour and len(self.expression.hour.parsed_values) == 1 and
                self.expression.day_of_month and len(self.expression.day_of_month.parsed_values) == 1 and
                self.expression.month and len(self.expression.month.parsed_values) == 1 and
                self.expression.day_of_week and self.expression.day_of_week.is_wildcard())

    def _get_field_name(self, field_type: FieldType) -> str:
        """Get human-readable field name."""
        names = {
            FieldType.MINUTE: "minute",
            FieldType.HOUR: "hour",
            FieldType.DAY_OF_MONTH: "day",
            FieldType.MONTH: "month",
            FieldType.DAY_OF_WEEK: "day_of_week"
        }
        return names.get(field_type, field_type.value)

    def _get_field_name_plural(self, field_type: FieldType) -> str:
        """Get human-readable plural field name."""
        names = {
            FieldType.MINUTE: "minutes",
            FieldType.HOUR: "hours",
            FieldType.DAY_OF_MONTH: "days",
            FieldType.MONTH: "months",
            FieldType.DAY_OF_WEEK: "days_of_week"
        }
        return names.get(field_type, field_type.value + "s")

    def _get_month_name(self, month: int) -> str:
        """Get month name from number."""
        months = ["", "January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        return months[month] if 0 < month <= 12 else str(month)

    def _get_weekday_name(self, day: int) -> str:
        """Get weekday name from number."""
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        return days[day] if 0 <= day <= 6 else str(day)

    def _get_single_weekday_name(self) -> str:
        """Get the single weekday name if only one is selected."""
        if self.expression.day_of_week and len(self.expression.day_of_week.parsed_values) == 1:
            day = list(self.expression.day_of_week.parsed_values)[0]
            return self._get_weekday_name(day)
        return ""