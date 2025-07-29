"""A puller for FRED data."""

# pylint: disable=global-statement,unused-argument
import logging
import os

import pandas as pd
from fredapi import Fred  # type: ignore
from requests_cache.session import CachedSession

_FRED_CLIENT = None


def _get_fred_client() -> Fred:
    global _FRED_CLIENT
    if _FRED_CLIENT is None:
        _FRED_CLIENT = Fred(api_key=os.environ["FRED_API_KEY"])
    return _FRED_CLIENT


def pull(series: str, session: CachedSession) -> list[pd.Series]:
    """Pull the FRED economic data."""
    logging.info("Pulling FRED series %s", series)
    series_name = "FRED_" + series
    client = _get_fred_client()
    try:
        df = client.get_series_all_releases(series)
    except ValueError:
        df = client.get_series(series)
        df.index = df.index.date  # type: ignore
        df = df.sort_index()
        return [df.rename(series_name)]
    df["date"] = pd.to_datetime(df["date"])
    df["realtime_start"] = pd.to_datetime(df["realtime_start"])

    def select_latest(group: pd.DataFrame) -> pd.DataFrame:
        return group[group["realtime_start"] == group["realtime_start"].max()]

    df = df.groupby("date").apply(select_latest)
    df = df.set_index("date")
    df.index = df.index.date  # type: ignore
    df = df.sort_index()
    return [df["value"].rename(series_name)]
