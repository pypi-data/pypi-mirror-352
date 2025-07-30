"""Find the args used by the main CLI."""

import argparse
import datetime

STDOUT_FILE = "-"


def _valid_date(s: str) -> datetime.date:
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"not a valid date: {s!r}") from exc


def parse_args() -> argparse.Namespace:
    """Create the args based on the CLI inputs."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        default=STDOUT_FILE,
        help="The file to write the output to (- if to stdout).",
    )
    parser.add_argument(
        "--min-date",
        required=False,
        help="The minimum date (YYYY-MM-DD) to consider when generating data.",
        type=_valid_date,
    )
    return parser.parse_args()
