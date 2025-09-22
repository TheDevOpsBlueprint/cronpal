#!/usr/bin/env python3
"""Main CLI entry point for CronPal."""

import sys
from datetime import datetime

from cronpal.error_handler import ErrorHandler, suggest_fix
from cronpal.exceptions import CronPalError
from cronpal.field_parser import FieldParser
from cronpal.models import CronExpression
from cronpal.parser import create_parser
from cronpal.scheduler import CronScheduler
from cronpal.special_parser import SpecialStringParser
from cronpal.validators import validate_expression, validate_expression_format


def main(args=None):
    """Main entry point for the cronpal CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Handle version flag
    if parsed_args.version:
        from cronpal import __version__
        print(f"cronpal {__version__}")
        return 0

    # Handle cron expression
    if parsed_args.expression:
        # Create error handler
        error_handler = ErrorHandler(verbose=parsed_args.verbose)

        try:
            # Validate the expression first
            validate_expression(parsed_args.expression)

            # Check if it's a special string
            special_parser = SpecialStringParser()
            if special_parser.is_special_string(parsed_args.expression):
                # Parse as special string
                cron_expr = special_parser.parse(parsed_args.expression)

                print(f"✓ Valid cron expression: {cron_expr}")

                if parsed_args.verbose:
                    print(f"  Special string: {cron_expr.raw_expression}")
                    description = special_parser.get_description(cron_expr.raw_expression)
                    print(f"  Description: {description}")

                    # For @reboot, we don't have fields to show
                    if cron_expr.raw_expression.lower() != "@reboot":
                        _print_verbose_fields(cron_expr)
            else:
                # Parse the expression into fields
                fields = validate_expression_format(parsed_args.expression)

                # Create a CronExpression object
                cron_expr = CronExpression(parsed_args.expression)

                # Parse all fields
                field_parser = FieldParser()
                cron_expr.minute = field_parser.parse_minute(fields[0])
                cron_expr.hour = field_parser.parse_hour(fields[1])
                cron_expr.day_of_month = field_parser.parse_day_of_month(fields[2])
                cron_expr.month = field_parser.parse_month(fields[3])
                cron_expr.day_of_week = field_parser.parse_day_of_week(fields[4])

                print(f"✓ Valid cron expression: {cron_expr}")

                if parsed_args.verbose:
                    print(f"  Raw expression: {cron_expr.raw_expression}")
                    print(f"  Validation: PASSED")
                    _print_verbose_fields(cron_expr)

            # Show next run times if requested
            if parsed_args.next is not None:
                _print_next_runs(cron_expr, parsed_args.next)

            return 0

        except CronPalError as e:
            # Use error handler for formatting
            error_handler.print_error(e, parsed_args.expression)

            # Suggest a fix if possible
            suggestion = suggest_fix(e, parsed_args.expression)
            if suggestion:
                print(f"  💡 Suggestion: {suggestion}", file=sys.stderr)

            return 1

        except Exception as e:
            # Handle unexpected errors
            error_handler.print_error(e, parsed_args.expression)
            return 2

    # If no arguments provided, show help
    parser.print_help()
    return 0


def _print_verbose_fields(cron_expr: CronExpression):
    """
    Print verbose field information.

    Args:
        cron_expr: The CronExpression to print fields for.
    """
    if cron_expr.minute:
        print(f"  Minute field: {cron_expr.minute.raw_value}")
        if cron_expr.minute.parsed_values:
            _print_field_values("    ", cron_expr.minute.parsed_values)

    if cron_expr.hour:
        print(f"  Hour field: {cron_expr.hour.raw_value}")
        if cron_expr.hour.parsed_values:
            _print_field_values("    ", cron_expr.hour.parsed_values)

    if cron_expr.day_of_month:
        print(f"  Day of month field: {cron_expr.day_of_month.raw_value}")
        if cron_expr.day_of_month.parsed_values:
            _print_field_values("    ", cron_expr.day_of_month.parsed_values)

    if cron_expr.month:
        print(f"  Month field: {cron_expr.month.raw_value}")
        if cron_expr.month.parsed_values:
            _print_field_values("    ", cron_expr.month.parsed_values)
            _print_month_names("    ", cron_expr.month.parsed_values)

    if cron_expr.day_of_week:
        print(f"  Day of week field: {cron_expr.day_of_week.raw_value}")
        if cron_expr.day_of_week.parsed_values:
            _print_field_values("    ", cron_expr.day_of_week.parsed_values)
            _print_day_names("    ", cron_expr.day_of_week.parsed_values)


def _print_field_values(prefix: str, values: set):
    """
    Print field values in a nice format.

    Args:
        prefix: Prefix for each line.
        values: Set of values to print.
    """
    sorted_values = sorted(values)
    if len(sorted_values) <= 10:
        print(f"{prefix}Values: {sorted_values}")
    else:
        print(f"{prefix}Values: {sorted_values[:5]} ... {sorted_values[-5:]}")
        print(f"{prefix}Total: {len(sorted_values)} values")


def _print_month_names(prefix: str, values: set):
    """
    Print month names for month values.

    Args:
        prefix: Prefix for each line.
        values: Set of month numbers to convert to names.
    """
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    sorted_values = sorted(values)
    names = [month_names[v - 1] for v in sorted_values if 1 <= v <= 12]

    if len(names) <= 10:
        print(f"{prefix}Months: {', '.join(names)}")


def _print_day_names(prefix: str, values: set):
    """
    Print day names for day of week values.

    Args:
        prefix: Prefix for each line.
        values: Set of day numbers to convert to names.
    """
    day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    sorted_values = sorted(values)
    names = [day_names[v] for v in sorted_values if 0 <= v <= 6]

    if len(names) <= 7:
        print(f"{prefix}Days: {', '.join(names)}")


def _print_next_runs(cron_expr: CronExpression, count: int):
    """
    Print the next run times for a cron expression.

    Args:
        cron_expr: The CronExpression to calculate runs for.
        count: Number of next runs to show.
    """
    # Don't show next runs for @reboot
    if cron_expr.raw_expression.lower() == "@reboot":
        print("\nNext runs: @reboot only runs at system startup")
        return

    # Make sure we have parsed fields
    if not cron_expr.is_valid():
        print("\nNext runs: Cannot calculate - incomplete expression")
        return

    try:
        scheduler = CronScheduler(cron_expr)
        next_runs = scheduler.get_next_runs(count)

        print(f"\nNext {count} run{'s' if count != 1 else ''}:")
        for i, run_time in enumerate(next_runs, 1):
            # Format the datetime nicely
            formatted = run_time.strftime("%Y-%m-%d %H:%M:%S %A")

            # Add relative time for first few entries
            if i <= 3:
                now = datetime.now()
                delta = run_time - now

                if delta.days == 0:
                    if delta.seconds < 3600:
                        minutes = delta.seconds // 60
                        relative = f"in {minutes} minute{'s' if minutes != 1 else ''}"
                    else:
                        hours = delta.seconds // 3600
                        relative = f"in {hours} hour{'s' if hours != 1 else ''}"
                elif delta.days == 1:
                    relative = "tomorrow"
                elif delta.days < 7:
                    relative = f"in {delta.days} days"
                else:
                    relative = ""

                if relative:
                    print(f"  {i}. {formatted} ({relative})")
                else:
                    print(f"  {i}. {formatted}")
            else:
                print(f"  {i}. {formatted}")

    except Exception as e:
        print(f"\nNext runs: Error calculating - {e}")


if __name__ == "__main__":
    sys.exit(main())