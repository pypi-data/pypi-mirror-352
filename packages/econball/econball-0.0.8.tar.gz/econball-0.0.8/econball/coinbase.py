"""A puller for coinbase data."""

# pylint: disable=unused-argument
import datetime
import logging

import pandas as pd
from cbhist.historical import fetch_historical  # type: ignore
from requests_cache.session import CachedSession


def pull(series: str, session: CachedSession) -> list[pd.Series]:
    """Pull the coinbase data."""
    logging.info("Pulling coinbase series %s", series)
    df = fetch_historical(series, 60 * 60 * 24, datetime.datetime(2000, 1, 1))
    df.index = df.index.date  # type: ignore
    df = df.sort_index()
    return [
        df["close"].rename(series + "_close"),
        df["volume"].rename(series + "_volume"),
    ]
