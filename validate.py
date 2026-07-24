"""
Milestone 3 runner: is the freight signal actually real?

    python validate.py

Runs the information-coefficient, Granger-causality, and out-of-sample tests and
prints an honest verdict. Uses the same cached price data as main.py.
"""
from src.ingest import download_prices
from src.signal import freight_score
from src.validate import run_report


def main():
    prices = download_prices()
    strength = freight_score(prices)
    run_report(prices, strength)


if __name__ == "__main__":
    main()
