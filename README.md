# Multi-Asset Portfolio VaR & Stress Testing Framework

A Python framework for measuring market risk on a multi-asset portfolio using
five Value-at-Risk methodologies plus Expected Shortfall, formal statistical
backtests, historical stress scenarios, Component VaR decomposition, and
Extreme Value Theory for the deep tail.

Built end-to-end from scratch (no pre-built VaR libraries) on 12 years of
daily data covering the 2020 COVID crash, the 2022 rate shock, and earlier
crises via extended history. The goal: not just compute VaR, but **validate**
it — the difference between an analytics exercise and a real risk project.

---

## Headline Results

On an equal-weighted 9-asset portfolio (US large/mid/small cap, international
equity, long Treasuries, high-yield credit, gold, oil, USD) over 2014-01-03
to 2026-05-28 (3,118 daily observations, equal weights):

**1. The fat-tail problem is real and measurable.** Parametric-Normal 99%
1-day VaR is **1.54%**; empirical Historical VaR is **1.80%** — a 17%
underestimate. Student-t and EVT methods close the gap.

**2. Out-of-sample backtests reveal which models are usable.** Plain
Historical, Parametric-Normal, and Monte-Carlo-Normal all fail
Christoffersen-independence at 95% (p ≈ 0.000) — they have the right
exceedance *rate* but cluster violations in the 2020 and 2022 stress windows.
At 99%, Parametric-Normal exceeds its threshold **2.41% of days** vs the
nominal 1.00%, failing Kupiec hard. **FHS with GARCH(1,1) is the only model
that passes both unconditional (Kupiec p = 0.55, 0.77) and conditional
(Christoffersen p = 0.96, 0.08) coverage at both confidence levels.**

**3. Stress tests show COVID > 2008 in velocity if not in size.** Current
portfolio re-priced under historical crises:

| Scenario | Days | Cumulative loss |
|---|---:|---:|
| 2020 COVID | 24 | 23.4% |
| 2008 Global Financial Crisis | 63 | 22.8% |
| 2018 Q4 vol | 63 | 10.9% |
| 2022 Rate Shock | 124 | 9.2% |

Both crises produced ~23% drawdowns, but COVID got there at 47% annualized
vol over a single quarter — 1.5× the GFC's pace.

**4. Risk decomposition shows equal weight ≠ equal risk.** USO (oil) at 11%
weight carries **23.8% of total VaR**. The five equity-like assets (SPY,
QQQ, IWM, EFA, USO) together = 55% of weight and 90% of risk. TLT and UUP
have **negative marginal VaR** — adding more of either *reduces* portfolio
risk. This is the input to risk-parity construction.

**5. EVT extends the analysis to events not in the sample.** A Generalized
Pareto fit to the 5%-worst losses gives **ξ = 0.31** (heavy tail confirmed).
Implied 99.9% VaR = **4.14%**, more than **2× the Parametric-Normal estimate
of ~2.05%** at the same confidence — a structural quantification of the
Gaussian model's tail underestimate.

---

## Key Figures

| File | What it shows |
|---|---|
| `figures/01_returns_histogram_var.png` | Empirical return distribution with overlaid 95% VaR lines from each method. Visual confirmation that the left tail is fatter than Gaussian. |
| `figures/02_var_method_comparison.png` | Side-by-side 95% and 99% VaR bars across five methods. The 99% panel shows the fat-tail divergence. |
| `figures/03_garch_conditional_vol.png` | Conditional volatility series from GARCH(1,1). Massive spikes during 2020 and 2022. |
| `figures/04_fhs_vs_hist_var.png` | **The money shot:** rolling 95% VaR — plain Historical vs Filtered Historical. FHS reacts immediately when vol spikes; plain HS lags by months. |
| `figures/05_fhs_vs_hist_covid_zoom.png` | Same comparison zoomed to Feb–Jun 2020. |
| `figures/06_backtest_95_violations.png` | Rolling 95% VaR per method with violation markers. Plain methods cluster failures around COVID. |
| `figures/07_backtest_99_violations.png` | Same at 99%. Normal methods over-exceed by 2.4×. |
| `figures/08_stress_scenarios.png` | Cumulative loss bars across 5 historical crises. |
| `figures/09_worst_scenario_contributions.png` | Per-asset contribution to the 2020 COVID loss. TLT and UUP saved ~2 percentage points. |
| `figures/10_component_var.png` | Equal weight vs % VaR contribution bars. USO is 11% weight, 24% of risk. |
| `figures/11_mean_excess.png` | EVT mean-excess function for threshold selection. |
| `figures/12_evt_vs_others.png` | VaR by confidence level — EVT vs Historical vs Normal. EVT extrapolates the deep tail. |

---

## Methodology

**Universe.** Nine ETFs spanning US equities (SPY, QQQ, IWM), international
equity (EFA), long-duration Treasuries (TLT), high-yield credit (HYG),
gold (GLD), oil (USO), and USD (UUP). Equal weights.

**Data.** Daily adjusted close prices from Yahoo Finance via `yfinance`,
cached to parquet for reproducibility.

**Methods implemented (all from scratch, no pre-built VaR libraries):**

| Method | Tail model | Key trade-off |
|---|---|---|
| Historical Simulation | Empirical (sorted history) | No assumption; can't extrapolate past sample |
| Variance-Covariance (Normal) | Closed-form Gaussian | Fast, but thin tails |
| Variance-Covariance (Student-t) | MLE-fit t | Captures kurtosis |
| Monte Carlo (MV-Normal) | 10k simulated draws | Slow, identical to Parametric for linear book |
| Monte Carlo (MV-Student-t) | 10k draws, fitted df | MV-Normal with fat tails |
| Filtered Historical (GARCH(1,1)) | Resampled GARCH residuals | Conditional on current vol |
| EVT (POT-GPD) | Generalized Pareto on excesses | Extrapolates past sample max |

**Backtesting.** Strictly out-of-sample with rolling 500-day window (1,000
for FHS), refitting GARCH every 60 trading days. Tests:
- Kupiec POF (unconditional coverage, χ²(1))
- Christoffersen independence (Markov-chain, χ²(1))
- Christoffersen conditional coverage (joint, χ²(2))
- Basel traffic-light zones

**Stress testing.** Current portfolio re-priced under actual daily returns
from five historical crisis windows (extended price history downloaded from
2007 for the 2008 GFC).

**Component VaR.** Euler decomposition of Parametric-Normal portfolio VaR
into per-asset contributions: MVaR_i = z_α (Σw)_i / σ_p, Component VaR_i =
w_i × MVaR_i. Sum across assets equals total portfolio VaR exactly.

**EVT.** Peaks-Over-Threshold with the 95th-percentile loss as threshold;
MLE-fit Generalized Pareto Distribution on the excesses.

---

## How to Run

Requires Python ≥ 3.9.

```bash
git clone https://github.com/John-Slye/portfolio_var_project.git
cd portfolio_var_project
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e . -r requirements.txt
python -m portfolio_var.data         # downloads + caches prices (~30s, once)
jupyter lab notebooks/01_walkthrough.ipynb
```

Then "Run All" — the full notebook executes in ~2 minutes.

---

## Project Structure

```
portfolio_var_project/
├── src/portfolio_var/
│   ├── data.py             # download + cache + returns computation
│   ├── var_methods.py      # Historical, Parametric, MC, FHS — VaR & ES
│   ├── backtesting.py      # Kupiec, Christoffersen, Basel; rolling VaR
│   ├── stress.py           # historical scenario re-pricing
│   ├── decomposition.py    # Component / Marginal VaR (Euler)
│   └── evt.py              # Peaks-Over-Threshold with GPD
├── notebooks/
│   └── 01_walkthrough.ipynb   # end-to-end story with discussion cells
├── figures/                # all 12 charts saved here
├── data/                   # cached parquet price files (regenerated by data.py)
├── tests/
├── pyproject.toml
└── requirements.txt
```

---

## Skills Demonstrated

Value at Risk (VaR), Expected Shortfall (CVaR), Historical Simulation,
Variance-Covariance, Monte Carlo simulation, Filtered Historical Simulation,
GARCH(1,1), Kupiec POF backtest, Christoffersen conditional-coverage backtest,
Basel traffic-light approach, historical stress testing, Component VaR /
Marginal VaR via Euler decomposition, Extreme Value Theory, Generalized
Pareto Distribution, Peaks-Over-Threshold method, Python software engineering
(modular package, reproducible notebooks, parquet caching), `numpy`,
`pandas`, `scipy.stats`, `arch`, `matplotlib`, `seaborn`.

---

## References

- Jorion, *Value at Risk: The New Benchmark for Managing Financial Risk*
- Hull, *Risk Management and Financial Institutions*, ch. 12–16
- McNeil, Frey & Embrechts, *Quantitative Risk Management* (EVT chapter for Phase 5)
- Basel Committee, *Supervisory Framework for the Use of "Backtesting" in Conjunction with the Internal Models Approach to Market Risk Capital Requirements*, 1996 (traffic-light zones)
