"""The CLI for executing the economics data pull."""

import io
import logging
import sys

from dotenv import load_dotenv

from . import __VERSION__
from .args import parse_args
from .pull import pull

_STDOUT_FILE = "-"


def main() -> None:
    """The main CLI function."""
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    logging.info("--- econball %s ---", __VERSION__)

    df = pull(min_date=args.min_date)
    logging.info(df)

    handle = io.BytesIO()
    df.to_parquet(handle, compression="gzip")
    handle.seek(0)
    if args.file == _STDOUT_FILE:
        sys.stdout.buffer.write(handle.getbuffer())
    else:
        with open(args.file, "wb") as fhandle:
            fhandle.write(handle.getbuffer())


if __name__ == "__main__":
    main()
