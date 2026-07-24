"""
Step 1: pull price data and cache it locally so we don't hammer the API.
Free data via yfinance. Everything downstream reads from the cache.
"""
import os
import pandas as pd
import yfinance as yf

from .universe import UNIVERSE, BENCHMARK, FREIGHT_TICKER, START_DATE, END_DATE

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CACHE = os.path.join(DATA_DIR, "prices.csv")


def download_prices(force=False):
    """Download daily adjusted close prices for the whole universe + benchmark."""
    if os.path.exists(CACHE) and not force:
        print(f"Loading cached prices from {CACHE}")
        return pd.read_csv(CACHE, index_col=0, parse_dates=True)

    tickers = list(UNIVERSE.keys()) + [BENCHMARK, FREIGHT_TICKER]
    print(f"Downloading {len(tickers)} tickers from yfinance...")
    raw = yf.download(
        tickers,
        start=START_DATE,
        end=END_DATE,
        auto_adjust=True,   # adjust for splits/dividends -- important for backtests
        progress=False,
    )
    # When multiple tickers are requested, columns are a MultiIndex (field, ticker).
    prices = raw["Close"].dropna(how="all")

    os.makedirs(DATA_DIR, exist_ok=True)
    prices.to_csv(CACHE)
    print(f"Saved {prices.shape[0]} rows x {prices.shape[1]} tickers to {CACHE}")
    return prices


if __name__ == "__main__":
    df = download_prices(force=True)
    print(df.tail())
