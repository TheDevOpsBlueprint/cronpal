#!/usr/bin/env python3
"""Main CLI entry point for CronPal."""

import sys

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
        try:
            # Validate the expression first
            validate_expression(parsed_args.expression)

            # Create a CronExpression object
            cron_expr = CronExpression(parsed_args.expression)
            print(f"✓ Valid cron expression: {cron_expr}")

            if parsed_args.verbose:
                print(f"Raw expression: {cron_expr.raw_expression}")
                print(f"Validation: PASSED")

            return 0

        except CronPalError as e:
            print(f"✗ Invalid cron expression: {e}", file=sys.stderr)
            if parsed_args.verbose:
                print(f"Expression: {parsed_args.expression}", file=sys.stderr)
            return 1

    # If no arguments provided, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())