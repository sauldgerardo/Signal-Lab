# signal-lab

A signal research engine for equity long-short strategies driven by **alternative
data**. It tests a real-world hypothesis with proper statistics and a
cost-aware backtest, so you can tell a genuine tradeable edge from noise.

## The current thesis
When global **freight / shipping costs spike**, retailers that import most of
their goods eat higher landed costs they can't fully pass on → margin squeeze.
The market is slow to reprice the lag. So we **short high-import** names and
**long low-import** names in a market-neutral book.

The point isn't that this one signal prints money — it's the *framework* and the
*rigor*: mechanism stated first, out-of-sample testing, honest net-of-cost stats.

## Quick start
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
This downloads prices, builds the long-short book, prints performance stats, and
saves `output/strategy_vs_spy.png`.

## Results so far
![conditional vs always-on vs SPY](output/strategy_vs_spy.png)

**Milestone 1 — always-on book.** Permanently short importers, long domestic
names, every day. It *underperforms*: freight wasn't elevated most of the window,
so the book spent years structurally short high-growth retailers through a bull
market — fighting the market, not trading the signal. Sharpe ≈ **-0.12**.

**Milestone 2 — conditional on freight.** The *same* book, but only turned on
when the freight proxy ([BDRY](https://www.breakwaveadvisors.com/), dry-bulk
freight futures) is elevated versus its own trailing year, acted on with a lag so
there's no look-ahead. The strategy sits flat ~58% of days and only leans against
importers when freight is actually stressed.

| Strategy (2019–2026, net of costs) | Ann. vol | Max drawdown | Sharpe |
|---|---|---|---|
| Milestone 1 (always-on) | 0.12 | -0.32 | -0.12 |
| **Milestone 2 (conditional)** | **0.05** | **-0.15** | -0.18 |

The gating **cut volatility ~60% and halved the drawdown** — a much healthier
risk profile — but the strategy is still *not* reliably profitable. That is the
honest state of it: conditioning fixed the risk, but whether the freight signal
has real predictive *edge* is a separate question. Answering it rigorously
(information coefficient, Granger causality, out-of-sample) is **Milestone 3** —
and a finding of "no edge" would be a legitimate, defensible result too.

## Milestone 3 — is the signal actually real?
A rising backtest curve is not evidence. `python validate.py` runs the tests a
quant would run before believing anything:

| Test | What it asks | Result |
|---|---|---|
| **Information Coefficient** | Does the stock ranking predict next-day returns? | IC ≈ **+0.001**, t ≈ 0.2 → **not significant** |
| — on freight-elevated days | Is it stronger when freight spikes (as the thesis says)? | IC ≈ +0.003 — *directionally right, still not significant* |
| **Granger causality** | Do freight moves *precede* the long-short spread? | best p ≈ **0.94** → **no lead/lag** |
| **Out-of-sample** | Does it survive an untouched 2nd half (post-2022)? | Sharpe **0.0 → −0.3** → **does not survive** |

**Verdict: no robust, statistically significant edge.** The freight→margin story
is real *economically*, but at this universe and daily frequency it does not
produce a tradeable signal. That's not a failure of the project — in real signal
research most ideas die exactly here, and being able to *prove* one is dead is
the skill. One honest crumb: the IC is slightly higher on freight-elevated days,
which is the direction the thesis predicts — just far too weak to trade.

**Where this could go next** (why it isn't a dead end): weekly instead of daily
frequency, a wider universe, a cleaner freight index (Freightos/Cass rather than
an ETF proxy), or company-level import-share data instead of hand-set scores.

## Layout
- `src/universe.py` — the stock list, the thesis, and per-stock import-exposure scores
- `src/ingest.py` — pull + cache price data (yfinance)
- `src/signal.py` — turn the freight proxy into a lagged, conditional signal
- `src/backtest.py` — long-short weights, always-on + conditional backtests, stats
- `src/validate.py` — information coefficient, Granger causality, out-of-sample tests
- `main.py` — runs the backtest comparison and chart
- `validate.py` — runs the Milestone 3 validation report

## Roadmap
1. **Milestone 1:** static thesis book vs. SPY, one chart. ✅
2. **Milestone 2:** dynamic signal — drive the book off a freight proxy (BDRY),
   with rolling z-score, lag handling, and turnover-based costs. ✅
3. **Milestone 3:** validation layer — information coefficient, Granger
   causality, out-of-sample split, significance tests. ✅
4. **Milestone 4:** Streamlit dashboard + a one-page written thesis.

## Honesty notes
Research tool, not live trading. Freight→margin effects are real but noisy —
expect a modest Sharpe, and report it honestly. That candor is what makes it
credible on a desk.
