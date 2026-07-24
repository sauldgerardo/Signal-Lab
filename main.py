"""
FIRST MILESTONE runner.

    python main.py

What it does:
  1. Downloads (and caches) prices for the stock universe + SPY.
  2. Builds a market-neutral long-short book from the import-exposure thesis.
  3. Backtests it and prints honest performance stats.
  4. Saves a chart of the strategy vs. SPY to output/strategy_vs_spy.png.

This is the skeleton. Everything else (dynamic freight signal, statistical
validation, Streamlit dashboard) hangs off this.
"""
import os
import matplotlib
matplotlib.use("Agg")  # save to file, no GUI needed
import matplotlib.pyplot as plt

from src.ingest import download_prices
from src.backtest import run_backtest, performance_stats

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


def main():
    prices = download_prices()
    results, weights = run_backtest(prices)

    print("\n--- LONG-SHORT WEIGHTS (positive = long, negative = short) ---")
    print(weights.sort_values().round(3).to_string())

    print("\n--- PERFORMANCE (net of a simple cost assumption) ---")
    for name in ["strategy", "benchmark"]:
        stats = performance_stats(results[name])
        print(f"\n{name.upper()}")
        for k, v in stats.items():
            print(f"  {k:15s}: {v}")

    # cumulative return chart
    curve = (1 + results).cumprod()
    plt.figure(figsize=(11, 6))
    plt.plot(curve.index, curve["strategy"], label="Long-Short strategy", linewidth=2)
    plt.plot(curve.index, curve["benchmark"], label="SPY (benchmark)", linewidth=1.5, alpha=0.7)
    plt.title("Freight-Exposure Long-Short vs. SPY (growth of $1)")
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
