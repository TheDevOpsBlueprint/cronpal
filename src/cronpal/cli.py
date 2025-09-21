#!/usr/bin/env python3
"""Main CLI entry point for CronPal."""

import sys

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

    # Handle cron expression (placeholder for now)
    if parsed_args.expression:
        print(f"Parsing cron expression: {parsed_args.expression}")
        return 0

    # If no arguments provided, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())