"""
Step 2: turn the import-exposure thesis into a market-neutral long-short
portfolio and see how it would have performed vs. the benchmark.

This is the FIRST-MILESTONE skeleton -- deliberately simple and readable so you
can defend every line. It is a static-weight backtest: weights come straight
from the hand-set exposure scores. Later milestones make the signal dynamic
(driven by live freight data) and add proper statistical validation.
"""
import numpy as np
import pandas as pd

from .universe import UNIVERSE, BENCHMARK


def build_weights():
    """
    Convert exposure scores into long-short weights.

    Long the LOW-exposure names, short the HIGH-exposure names.
    Center the scores so the book is roughly dollar-neutral (longs ~= shorts),
    which isolates the SIGNAL from broad market moves.
    """
    scores = pd.Series({t: s for t, (s, _) in UNIVERSE.items()})
    centered = scores - scores.mean()
    # negative weight on high-exposure (short), positive on low-exposure (long)
    weights = -centered
    # scale so total gross exposure (sum of |weights|) = 1.0
    weights = weights / weights.abs().sum()
    return weights


def run_backtest(prices, cost_per_turnover=0.0005):
    """
    Static-weight daily backtest.

    cost_per_turnover: round-trip transaction cost assumption (5 bps default).
    For a static book this only hits us on day one, but we keep the hook so the
    dynamic version stays honest about costs.
    """
    weights = build_weights()
    tickers = weights.index.tolist()

    rets = prices[tickers].pct_change().dropna()
    # portfolio daily return = weighted sum of stock returns
    strat = (rets * weights).sum(axis=1)

    # one-time cost of putting the book on
    strat.iloc[0] -= weights.abs().sum() * cost_per_turnover

    bench = prices[BENCHMARK].pct_change().reindex(strat.index).fillna(0)

    out = pd.DataFrame({"strategy": strat, "benchmark": bench})
    return out, weights


def performance_stats(returns, periods_per_year=252):
    """Sharpe, annualised return/vol, max drawdown, hit rate. Be honest."""
    ann_ret = returns.mean() * periods_per_year
    ann_vol = returns.std() * np.sqrt(periods_per_year)
    sharpe = ann_ret / ann_vol if ann_vol > 0 else np.nan
    curve = (1 + returns).cumprod()
    drawdown = (curve / curve.cummax() - 1).min()
    hit = (returns > 0).mean()
    return {
        "annual_return": round(ann_ret, 4),
        "annual_vol": round(ann_vol, 4),
        "sharpe": round(sharpe, 2),
        "max_drawdown": round(drawdown, 4),
        "hit_rate": round(hit, 3),
    }
