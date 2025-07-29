"""An enumeration for the different data sources in econball."""

from enum import StrEnum, auto


class Data(StrEnum):
    """Data enumeration."""

    FRED = auto()
    YFINANCE = auto()
    COINBASE = auto()
    EFD = auto()
