# CronPal

A command-line tool for parsing, validating, and analyzing cron expressions.

## Features (In Development)

- Parse and validate cron expressions
- Show next run times
- Pretty-print crontab entries
- Human-readable descriptions
- Cross-platform (macOS and Linux)

## Installation

```bash
# Development installation
pip install -e .
```

## Usage

```bash
cronpal "0 0 * * *"  # Parse and display cron expression
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT
