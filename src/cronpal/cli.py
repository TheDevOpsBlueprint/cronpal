#!/usr/bin/env python3
"""Main CLI entry point for CronPal."""

import sys
from datetime import datetime

from cronpal.color_utils import (
    ColorConfig,
    format_error_message,
    format_success_message,
    get_color_config,
    set_color_config,
)
from cronpal.error_handler import ErrorHandler, suggest_fix
from cronpal.exceptions import CronPalError
from cronpal.field_parser import FieldParser
from cronpal.models import CronExpression
from cronpal.parser import create_parser
from cronpal.pretty_printer import PrettyPrinter
from cronpal.scheduler import CronScheduler
from cronpal.special_parser import SpecialStringParser
from cronpal.timezone_utils import (
    format_datetime_with_timezone,
    get_current_time,
    get_timezone,
    get_timezone_abbreviation,
    get_timezone_offset,
    list_common_timezones,
)
from cronpal.validators import validate_expression, validate_expression_format


def main(args=None):
    """Main entry point for the cronpal CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Initialize color configuration
    use_colors = not getattr(parsed_args, 'no_color', False)
    color_config = ColorConfig(use_colors=use_colors)
    set_color_config(color_config)

    # Handle version flag
    if parsed_args.version:
        from cronpal import __version__
        print(color_config.info(f"cronpal {__version__}"))
        return 0

    # Handle list timezones flag
    if parsed_args.list_timezones:
        print(color_config.header("Available timezones:"))
        timezones = list_common_timezones()
        for tz in timezones:
            print(f"  {color_config.value(tz)}")
        print(f"\n{color_config.info(f'Total: {len(timezones)} timezones')}")
        return 0

    # Handle cron expression
    if parsed_args.expression:
        # Create error handler
        error_handler = ErrorHandler(verbose=parsed_args.verbose)

        try:
            # Get timezone if specified
            timezone = None
            if parsed_args.timezone:
                try:
                    timezone = get_timezone(parsed_args.timezone)
                    current_time = get_current_time(timezone)
                    tz_offset = get_timezone_offset(timezone, current_time)
                    tz_abbrev = get_timezone_abbreviation(timezone, current_time)
                    tz_info = f"{parsed_args.timezone} ({tz_abbrev} {tz_offset})"
                    print(color_config.info(f"Using timezone: {tz_info}"))
                except ValueError as e:
                    raise CronPalError(f"Invalid timezone: {e}")

            # Validate the expression first
            validate_expression(parsed_args.expression)

            # Check if it's a special string
            special_parser = SpecialStringParser()
            if special_parser.is_special_string(parsed_args.expression):
                # Parse as special string
                cron_expr = special_parser.parse(parsed_args.expression)

                if parsed_args.pretty:
                    # Pretty print mode
                    if cron_expr.raw_expression.lower() == "@reboot":
                        print(format_success_message(
                            f"Valid cron expression: {cron_expr.raw_expression}",
                            "This expression runs at system startup/reboot only."
                        ))
                    else:
                        printer = PrettyPrinter(cron_expr, use_colors=use_colors)
                        print()
                        print(printer.print_table())
                        print()
                        print(color_config.header("Summary: ") +
                              color_config.info(printer.get_summary()))

                        if parsed_args.verbose:
                            print()
                            print(printer.print_detailed())
                else:
                    # Normal output
                    print(format_success_message(
                        f"Valid cron expression: {cron_expr.raw_expression}"
                    ))

                    if parsed_args.verbose:
                        print(f"  {color_config.field('Special string')}: "
                              f"{color_config.value(cron_expr.raw_expression)}")
                        description = special_parser.get_description(cron_expr.raw_expression)
                        print(f"  {color_config.field('Description')}: "
                              f"{color_config.info(description)}")

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

                if parsed_args.pretty:
                    # Pretty print mode
                    printer = PrettyPrinter(cron_expr, use_colors=use_colors)
                    print()
                    print(printer.print_table())
                    print()
                    print(color_config.header("Summary: ") +
                          color_config.info(printer.get_summary()))

                    if parsed_args.verbose:
                        print()
                        print(printer.print_detailed())
                else:
                    # Normal output
                    print(format_success_message(
                        f"Valid cron expression: {cron_expr.raw_expression}"
                    ))

                    if parsed_args.verbose:
                        print(f"  {color_config.field('Raw expression')}: "
                              f"{color_config.value(cron_expr.raw_expression)}")
                        print(f"  {color_config.field('Validation')}: "
                              f"{color_config.success('PASSED')}")
                        _print_verbose_fields(cron_expr)

            # Show next run times if requested
            if parsed_args.next is not None:
                _print_next_runs(cron_expr, parsed_args.next, timezone)

            # Show previous run times if requested
            if parsed_args.previous is not None:
                _print_previous_runs(cron_expr, parsed_args.previous, timezone)

            return 0

        except CronPalError as e:
            # Use error handler for formatting
            print(format_error_message(str(e)), file=sys.stderr)

            # Suggest a fix if possible
            suggestion = suggest_fix(e, parsed_args.expression)
            if suggestion:
                color_config = get_color_config()
                print(f"  {color_config.warning('💡 Suggestion:')} {suggestion}",
                      file=sys.stderr)

            return 1

        except Exception as e:
            # Handle unexpected errors
            print(format_error_message(f"Unexpected error: {e}"), file=sys.stderr)
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
    config = get_color_config()

    if cron_expr.minute:
        print(f"  {config.field('Minute field')}: "
              f"{config.value(cron_expr.minute.raw_value)}")
        if cron_expr.minute.parsed_values:
            _print_field_values("    ", cron_expr.minute.parsed_values)

    if cron_expr.hour:
        print(f"  {config.field('Hour field')}: "
              f"{config.value(cron_expr.hour.raw_value)}")
        if cron_expr.hour.parsed_values:
            _print_field_values("    ", cron_expr.hour.parsed_values)

    if cron_expr.day_of_month:
        print(f"  {config.field('Day of month field')}: "
              f"{config.value(cron_expr.day_of_month.raw_value)}")
        if cron_expr.day_of_month.parsed_values:
            _print_field_values("    ", cron_expr.day_of_month.parsed_values)

    if cron_expr.month:
        print(f"  {config.field('Month field')}: "
              f"{config.value(cron_expr.month.raw_value)}")
        if cron_expr.month.parsed_values:
            _print_field_values("    ", cron_expr.month.parsed_values)
            _print_month_names("    ", cron_expr.month.parsed_values)

    if cron_expr.day_of_week:
        print(f"  {config.field('Day of week field')}: "
              f"{config.value(cron_expr.day_of_week.raw_value)}")
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
    config = get_color_config()
    sorted_values = sorted(values)
    if len(sorted_values) <= 10:
        values_str = str(sorted_values)
        print(f"{prefix}{config.field('Values')}: {config.value(values_str)}")
    else:
        truncated = f"{sorted_values[:5]} ... {sorted_values[-5:]}"
        print(f"{prefix}{config.field('Values')}: {config.value(truncated)}")
        print(f"{prefix}{config.field('Total')}: "
              f"{config.highlight(f'{len(sorted_values)} values')}")


def _print_month_names(prefix: str, values: set):
    """
    Print month names for month values.

    Args:
        prefix: Prefix for each line.
        values: Set of month numbers to convert to names.
    """
    config = get_color_config()
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    sorted_values = sorted(values)
    names = [month_names[v - 1] for v in sorted_values if 1 <= v <= 12]

    if len(names) <= 10:
        print(f"{prefix}{config.field('Months')}: "
              f"{config.info(', '.join(names))}")


def _print_day_names(prefix: str, values: set):
    """
    Print day names for day of week values.

    Args:
        prefix: Prefix for each line.
        values: Set of day numbers to convert to names.
    """
    config = get_color_config()
    day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    sorted_values = sorted(values)
    names = [day_names[v] for v in sorted_values if 0 <= v <= 6]

    if len(names) <= 7:
        print(f"{prefix}{config.field('Days')}: "
              f"{config.info(', '.join(names))}")


def _print_next_runs(cron_expr: CronExpression, count: int, timezone=None):
    """
    Print the next run times for a cron expression.

    Args:
        cron_expr: The CronExpression to calculate runs for.
        count: Number of next runs to show.
        timezone: Optional timezone for calculations.
    """
    config = get_color_config()

    # Don't show next runs for @reboot
    if cron_expr.raw_expression.lower() == "@reboot":
        print(f"\n{config.warning('Next runs: @reboot only runs at system startup')}")
        return

    # Make sure we have parsed fields
    if not cron_expr.is_valid():
        print(f"\n{config.error('Next runs: Cannot calculate - incomplete expression')}")
        return

    try:
        scheduler = CronScheduler(cron_expr, timezone)
        next_runs = scheduler.get_next_runs(count)

        print(f"\n{config.header(f'Next {count} run')}{'s' if count != 1 else ''}:")
        for i, run_time in enumerate(next_runs, 1):
            # Format the datetime with timezone info
            if timezone:
                formatted = format_datetime_with_timezone(run_time, timezone)
            else:
                formatted = run_time.strftime("%Y-%m-%d %H:%M:%S %A")

            # Add relative time for first few entries
            if i <= 3:
                now = get_current_time(timezone)
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
                    print(f"  {config.value(f'{i}.')} "
                          f"{config.highlight(formatted)} "
                          f"{config.separator('(')}({config.info(relative)}){config.separator(')')}")
                else:
                    print(f"  {config.value(f'{i}.')} {config.highlight(formatted)}")
            else:
                print(f"  {config.value(f'{i}.')} {config.highlight(formatted)}")

    except Exception as e:
        print(f"\n{config.error(f'Next runs: Error calculating - {e}')}")


def _print_previous_runs(cron_expr: CronExpression, count: int, timezone=None):
    """
    Print the previous run times for a cron expression.

    Args:
        cron_expr: The CronExpression to calculate runs for.
        count: Number of previous runs to show.
        timezone: Optional timezone for calculations.
    """
    config = get_color_config()

    # Don't show previous runs for @reboot
    if cron_expr.raw_expression.lower() == "@reboot":
        print(f"\n{config.warning('Previous runs: @reboot only runs at system startup')}")
        return

    # Make sure we have parsed fields
    if not cron_expr.is_valid():
        print(f"\n{config.error('Previous runs: Cannot calculate - incomplete expression')}")
        return

    try:
        scheduler = CronScheduler(cron_expr, timezone)
        previous_runs = scheduler.get_previous_runs(count)

        print(f"\n{config.header(f'Previous {count} run')}{'s' if count != 1 else ''} "
              f"{config.info('(most recent first)')}:")
        for i, run_time in enumerate(previous_runs, 1):
            # Format the datetime with timezone info
            if timezone:
                formatted = format_datetime_with_timezone(run_time, timezone)
            else:
                formatted = run_time.strftime("%Y-%m-%d %H:%M:%S %A")

            # Add relative time for first few entries
            if i <= 3:
                now = get_current_time(timezone)
                delta = now - run_time

                if delta.days == 0:
                    if delta.seconds < 3600:
                        minutes = delta.seconds // 60
                        relative = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                    else:
                        hours = delta.seconds // 3600
                        relative = f"{hours} hour{'s' if hours != 1 else ''} ago"
                elif delta.days == 1:
                    relative = "yesterday"
                elif delta.days < 7:
                    relative = f"{delta.days} days ago"
                else:
                    relative = ""

                if relative:
                    print(f"  {config.value(f'{i}.')} "
                          f"{config.info(formatted)} "
                          f"{config.separator('(')}({config.warning(relative)}){config.separator(')')}")
                else:
                    print(f"  {config.value(f'{i}.')} {config.info(formatted)}")
            else:
                print(f"  {config.value(f'{i}.')} {config.info(formatted)}")

    except Exception as e:
        print(f"\n{config.error(f'Previous runs: Error calculating - {e}')}")


if __name__ == "__main__":
    sys.exit(main())