#!/usr/bin/env python3
"""Main CLI entry point for CronPal."""

import sys

from cronpal.models import CronExpression
from cronpal.parser import create_parser


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
        # Create a CronExpression object
        cron_expr = CronExpression(parsed_args.expression)
        print(f"Parsing cron expression: {cron_expr}")

        if parsed_args.verbose:
            print(f"Raw expression: {cron_expr.raw_expression}")
            print(f"Valid: {cron_expr.is_valid()}")

        return 0

    # If no arguments provided, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())