"""
Milestone 3: does the signal actually have predictive EDGE, or is the backtest
just noise? A curve going up is not evidence. These are the tests a quant
researcher would run before believing anything.

  1. Information Coefficient (IC) -- across stocks, does our ranking (long the
     low-import names, short the high-import) actually line up with next-day
     returns? And is it STRONGER on days freight is elevated, like the thesis says?
  2. Granger causality -- do freight moves statistically PRECEDE the importer-vs-
     domestic return spread? (Correlation isn't causation; this is a lead/lag test.)
  3. Out-of-sample -- split the history in two. Does anything that looked good in
     the first half survive, untouched, in the second half?

Every number comes with a significance check (t-stat / p-value) so we don't fool
ourselves. A verdict of "no robust edge" is a legitimate, honest result.
"""
import warnings
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import grangercausalitytests

from .universe import FREIGHT_TICKER, BENCHMARK
from .backtest import build_weights, run_conditional_backtest, performance_stats


def _tstat(series):
    """t-stat of the mean of a return series being different from zero."""
    s = series.dropna()
    if len(s) < 3 or s.std() == 0:
        return np.nan
    return s.mean() / (s.std() / np.sqrt(len(s)))


def information_coefficient(prices, strength, on_threshold=0.05):
    """
    Daily cross-sectional IC: rank-correlation between our per-stock signal
    (long weight) and each stock's NEXT-day return, across the universe.

    Positive mean IC => the ranking predicts. We also split by whether freight
    was 'on' that day -- the thesis predicts a stronger (more positive) IC when
    freight is elevated.
    """
    long_w = build_weights()                       # positive = long, negative = short
    sig_rank = long_w.rank()                        # fixed cross-sectional ranking
    tickers = long_w.index.tolist()

    fwd = prices[tickers].pct_change().shift(-1)    # next-day return per stock
    fwd_rank = fwd.rank(axis=1)                      # rank across stocks each day

    # Spearman IC each day = Pearson on the ranks (pandas aligns by ticker, skips NaN)
    daily_ic = fwd_rank.apply(lambda row: row.corr(sig_rank), axis=1).dropna()

    freight_on = strength.reindex(daily_ic.index).fillna(0) > on_threshold

    return {
        "ic_all":       (daily_ic.mean(), _tstat(daily_ic), len(daily_ic)),
        "ic_freight_on":  (daily_ic[freight_on].mean(),  _tstat(daily_ic[freight_on]),  int(freight_on.sum())),
        "ic_freight_off": (daily_ic[~freight_on].mean(), _tstat(daily_ic[~freight_on]), int((~freight_on).sum())),
    }


def spread_series(prices):
    """The long-short 'spread' return: what the always-on book earns each day.
    Positive = low-import names beat high-import names that day."""
    long_w = build_weights()
    rets = prices[long_w.index].pct_change()
    return (rets * long_w).sum(axis=1)


def granger_causality(prices, maxlag=5):
    """
    Test whether CHANGES in freight cost Granger-cause the long-short spread.
    Uses stationary series (pct changes / returns). Reports the smallest p-value
    across lags 1..maxlag. p < 0.05 => freight leads the spread at some horizon.
    """
    freight_chg = prices[FREIGHT_TICKER].pct_change()
    spread = spread_series(prices)

    df = pd.concat([spread, freight_chg], axis=1).dropna()
    df.columns = ["spread", "freight_chg"]
    # grangercausalitytests(x[:, [y, x]]) tests whether the 2nd col causes the 1st
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = grangercausalitytests(df[["spread", "freight_chg"]], maxlag=maxlag)

    pvals = {lag: round(res[lag][0]["ssr_ftest"][1], 4) for lag in res}
    best_lag = min(pvals, key=pvals.get)
    return pvals, best_lag, pvals[best_lag]


def out_of_sample(prices, strength):
    """Split the freight window in half; run the conditional strategy on each.
    An edge that's real should show up in BOTH halves, not just one."""
    valid = strength.dropna()
    dates = prices.loc[valid.index.min():].index
    mid = dates[len(dates) // 2]

    results = {}
    for name, sl in [("in-sample (1st half)", slice(None, mid)),
                     ("out-of-sample (2nd half)", slice(mid, None))]:
        p = prices.loc[sl]
        bt, _, _ = run_conditional_backtest(p, strength)
        results[name] = performance_stats(bt["strategy"])
    return results, mid


def run_report(prices, strength):
    print("=" * 62)
    print("MILESTONE 3: SIGNAL VALIDATION")
    print("=" * 62)

    print("\n[1] INFORMATION COEFFICIENT  (mean daily rank-corr of signal vs next-day return)")
    print("    Positive = ranking predicts. Thesis: 'freight on' should be higher.")
    ic = information_coefficient(prices, strength)
    for k, (mean_ic, t, n) in ic.items():
        flag = "significant" if abs(t) > 1.96 else "not significant"
        print(f"    {k:16s}: IC={mean_ic:+.4f}   t={t:+.2f} ({flag})   n={n}")

    print("\n[2] GRANGER CAUSALITY  (does a freight move PRECEDE the long-short spread?)")
    pvals, best_lag, best_p = granger_causality(prices)
    print(f"    p-value by lag (days): {pvals}")
    verdict = "freight LEADS the spread" if best_p < 0.05 else "no lead/lag relationship"
    print(f"    best: lag {best_lag}, p={best_p}  ->  {verdict}")

    print("\n[3] OUT-OF-SAMPLE  (does the conditional strategy survive an untouched 2nd half?)")
    oos, mid = out_of_sample(prices, strength)
    print(f"    split at {mid.date()}")
    for name, s in oos.items():
        print(f"    {name:26s}: Sharpe={s['sharpe']:+.2f}  ann_ret={s['annual_return']:+.4f}  maxDD={s['max_drawdown']}")

    print("\n" + "-" * 62)
    print("HONEST VERDICT")
    print("-" * 62)
    ic_on = ic["ic_freight_on"]
    edge = (abs(ic_on[1]) > 1.96 and ic_on[0] > 0) or best_p < 0.05
    if edge:
        print("  Some statistically meaningful structure showed up. Worth pursuing")
        print("  further, but treat as a lead, not a proven money-maker.")
    else:
        print("  No robust, statistically significant edge survived the tests.")
        print("  The freight->margin story is real economically, but at this")
        print("  universe/frequency it doesn't produce a tradeable signal. In real")
        print("  research most signals die here -- reporting that honestly is the")
        print("  point, and it's a defensible conclusion.")
