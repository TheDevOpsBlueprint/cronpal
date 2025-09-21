#!/usr/bin/env python3
"""Main CLI entry point for CronPal."""

import sys

from cronpal.error_handler import ErrorHandler, suggest_fix
from cronpal.exceptions import CronPalError
from cronpal.field_parser import FieldParser
from cronpal.models import CronExpression
from cronpal.parser import create_parser
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

            # Parse the expression into fields
            fields = validate_expression_format(parsed_args.expression)

            # Create a CronExpression object
            cron_expr = CronExpression(parsed_args.expression)

            # Parse minute field if not a special expression
            if len(fields) == 5:
                field_parser = FieldParser()
                cron_expr.minute = field_parser.parse_minute(fields[0])

            print(f"✓ Valid cron expression: {cron_expr}")

            if parsed_args.verbose:
                print(f"  Raw expression: {cron_expr.raw_expression}")
                print(f"  Validation: PASSED")

                if cron_expr.minute:
                    print(f"  Minute field: {cron_expr.minute.raw_value}")
                    if cron_expr.minute.parsed_values:
                        values = sorted(cron_expr.minute.parsed_values)
                        if len(values) <= 10:
                            print(f"    Values: {values}")
                        else:
                            print(f"    Values: {values[:5]} ... {values[-5:]}")
                            print(f"    Total: {len(values)} values")

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


if __name__ == "__main__":
    sys.exit(main())