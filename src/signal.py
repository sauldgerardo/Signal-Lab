"""
Milestone 2: the CONDITIONAL freight signal.

Milestone 1's book was always-on -- it bet against importers every single day,
even when freight was cheap. That's why it fought the market and lost.

The thesis only applies WHEN FREIGHT IS ELEVATED. So here we turn the freight
proxy (BDRY) into a daily "how stressed is freight right now?" score, and later
use it to scale the long-short book up (freight spiking) or down to flat
(freight normal).

Two things that keep this honest / interview-defensible:
  1. Z-SCORE vs a trailing window -- "elevated" means high relative to its own
     recent history, not an absolute level.
  2. A LAG -- we only act on freight information from `lag_days` ago, so we never
     trade on data we couldn't actually have seen in real time (no look-ahead).
"""
import numpy as np
import pandas as pd

from .universe import FREIGHT_TICKER


def freight_score(prices, lookback=252, lag_days=5, cap=2.0):
    """
    Return a daily signal strength in [0, 1] from the freight proxy.

    lookback : trailing window (~1 year) for the rolling mean/std of the z-score.
    lag_days : trading-day delay before we act on freight info (no look-ahead,
               plus reflects that margin effects show up with a lag).
    cap      : z-score at which the signal is considered "fully on" (z >= cap
               -> strength 1.0). Only POSITIVE z (freight above normal) turns the
               book on; when freight is normal/cheap the strength is ~0 (flat).

    Returns a pd.Series aligned to the price index.
    """
    freight = prices[FREIGHT_TICKER].dropna()

    # rolling z-score: how unusual is today's freight cost vs the last year?
    roll_mean = freight.rolling(lookback).mean()
    roll_std = freight.rolling(lookback).std()
    z = (freight - roll_mean) / roll_std

    # only act on ELEVATED freight; scale 0 -> 1 up to the cap
    strength = z.clip(lower=0, upper=cap) / cap

    # LAG: shift forward so today's position uses freight info from lag_days ago
    strength = strength.shift(lag_days)

    return strength.reindex(prices.index)
