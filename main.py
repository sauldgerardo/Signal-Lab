"""
Runner: builds the strategy end-to-end and compares milestones.

    python main.py

  Milestone 1  = always-on long-short book (bets against importers every day).
  Milestone 2  = the SAME book, but only turned on when the freight signal says
                 shipping costs are actually elevated (conditional + lagged).

Both are compared against SPY over the window where freight data exists, so it's
apples to apples. Saves a chart to output/strategy_vs_spy.png.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.ingest import download_prices
from src.signal import freight_score
from src.backtest import (
    run_backtest, run_conditional_backtest, performance_stats,
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def print_stats(label, returns):
    stats = performance_stats(returns)
    print(f"\n{label}")
    for k, v in stats.items():
        print(f"  {k:15s}: {v}")


def main():
    prices = download_prices()

    # --- freight signal ---
    strength = freight_score(prices)

    # only compare over the window where the freight signal is actually defined
    # (BDRY history + rolling lookback + lag), so nothing gets a free head start
    valid = strength.dropna()
    start = valid.index.min()
    prices_w = prices.loc[start:]
    print(f"Freight signal available from {start.date()} -> comparing from there.")

    # --- Milestone 1: always-on book ---
    m1, _ = run_backtest(prices_w)

    # --- Milestone 2: conditional book ---
    m2, weights, strength_w = run_conditional_backtest(prices_w, strength)

    # align all three series to a common window
    idx = m2.index.intersection(m1.index)
    m1, m2 = m1.loc[idx], m2.loc[idx]

    print("\n================ PERFORMANCE (net of costs) ================")
    print_stats("SPY (benchmark)", m2["benchmark"])
    print_stats("Milestone 1  (always-on)", m1["strategy"])
    print_stats("Milestone 2  (conditional on freight)", m2["strategy"])

    days_on = (strength_w.loc[idx] > 0.05).mean()
    print(f"\nMilestone 2 was meaningfully 'on' {days_on:.0%} of days "
          f"(flat the rest -> that's the point).")

    # --- chart ---
    curve_m1 = (1 + m1["strategy"]).cumprod()
    curve_m2 = (1 + m2["strategy"]).cumprod()
    curve_spy = (1 + m2["benchmark"]).cumprod()

    plt.figure(figsize=(11, 6))
    plt.plot(curve_m2.index, curve_m2, label="Milestone 2: conditional on freight", linewidth=2.2)
    plt.plot(curve_m1.index, curve_m1, label="Milestone 1: always-on", linewidth=1.5, alpha=0.8)
    plt.plot(curve_spy.index, curve_spy, label="SPY (benchmark)", linewidth=1.5, alpha=0.6)
    plt.title("Freight-Exposure Long-Short: conditional vs. always-on vs. SPY (growth of $1)")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "strategy_vs_spy.png")
    plt.savefig(out_path, dpi=130)
    print(f"\nChart saved to {out_path}")


if __name__ == "__main__":
    main()
