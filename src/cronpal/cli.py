#!/usr/bin/env python3
"""Main CLI entry point for CronPal."""

import sys

from cronpal.error_handler import ErrorHandler, suggest_fix
from cronpal.exceptions import CronPalError
from cronpal.models import CronExpression
from cronpal.parser import create_parser
from cronpal.validators import validate_expression


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

            # Create a CronExpression object
            cron_expr = CronExpression(parsed_args.expression)
            print(f"✓ Valid cron expression: {cron_expr}")

            if parsed_args.verbose:
                print(f"  Raw expression: {cron_expr.raw_expression}")
                print(f"  Validation: PASSED")

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