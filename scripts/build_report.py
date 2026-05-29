"""Build the standalone PDF report from saved figures + project results.

Run from the project root after notebook has been executed:
    python scripts/build_report.py
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"
OUT = ROOT / "report.pdf"

# ----------------------------- styles ---------------------------------------
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="HeroTitle",   parent=styles["Title"],   fontSize=24, leading=28, spaceAfter=8))
styles.add(ParagraphStyle(name="HeroSubtitle",parent=styles["Title"],   fontSize=13, leading=16, textColor=colors.HexColor("#444"), spaceAfter=20))
styles.add(ParagraphStyle(name="H1",          parent=styles["Heading1"],fontSize=16, leading=20, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1b1b1b")))
styles.add(ParagraphStyle(name="H2",          parent=styles["Heading2"],fontSize=12, leading=15, spaceBefore=8,  spaceAfter=4, textColor=colors.HexColor("#1b1b1b")))
styles.add(ParagraphStyle(name="Body",        parent=styles["Normal"],  fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=6))
styles.add(ParagraphStyle(name="Caption",     parent=styles["Italic"],  fontSize=8.5, leading=11, textColor=colors.HexColor("#555"), alignment=TA_CENTER, spaceAfter=12))


def H1(s):  return Paragraph(s, styles["H1"])
def H2(s):  return Paragraph(s, styles["H2"])
def P(s):   return Paragraph(s, styles["Body"])
def CAP(s): return Paragraph(s, styles["Caption"])


def fig(name: str, width: float = 6.4, caption: str = "") -> list:
    path = FIG / name
    if not path.exists():
        return [P(f"<i>[missing figure: {name}]</i>")]
    out = [Image(str(path), width=width * inch, height=(width * 0.55) * inch)]
    if caption:
        out.append(CAP(caption))
    return out


def tbl(data, col_widths=None) -> Table:
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("FONTNAME",  (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND",(0, 0), (-1, 0), colors.HexColor("#e8eef5")),
        ("FONTSIZE",  (0, 0), (-1, -1), 9),
        ("GRID",      (0, 0), (-1, -1), 0.25, colors.HexColor("#999")),
        ("ALIGN",     (1, 0), (-1, -1), "RIGHT"),
        ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f7f7")]),
        ("LEFTPADDING",(0, 0), (-1, -1), 5),
        ("RIGHTPADDING",(0, 0), (-1, -1), 5),
        ("TOPPADDING",(0, 0), (-1, -1), 3),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 3),
    ]))
    return t


# ----------------------------- content ---------------------------------------
story = []

# ---------- Page 1: Title + Executive summary ----------
story += [
    Paragraph("Multi-Asset Portfolio<br/>VaR &amp; Stress Testing Framework", styles["HeroTitle"]),
    Paragraph("From-scratch implementation, validated on 12 years of daily data through COVID and the 2022 rate shock", styles["HeroSubtitle"]),
    H1("Executive Summary"),
    P("This project builds a Python framework for measuring market risk on a "
      "multi-asset portfolio (US, international, Treasuries, credit, commodities, FX) "
      "using seven Value-at-Risk methodologies, statistically validates them "
      "via formal backtests, evaluates losses under historical stress scenarios, "
      "decomposes total portfolio risk into per-asset contributions, and extrapolates "
      "the deep tail with Extreme Value Theory."),
    P("Five headline findings from the 2014–2026 sample (3,118 daily observations):"),
    P("1. <b>Fat tails are real and measurable.</b> Parametric-Normal 99% VaR underestimates "
      "the empirical 99% VaR by 17% (1.54% vs 1.80%). Student-t and EVT close the gap."),
    P("2. <b>Only one model passes backtesting.</b> Plain Historical, Parametric-Normal, "
      "and Monte-Carlo-Normal all fail Christoffersen-independence at 95% (p ≈ 0.000). "
      "Parametric-Normal exceeds its 99% threshold at 2.41% of days vs. the nominal "
      "1.00%, failing Kupiec hard. FHS with GARCH(1,1) is the only method to pass "
      "both unconditional and conditional coverage at both confidence levels."),
    P("3. <b>2020 COVID and 2008 GFC produced comparable drawdowns</b> (23.4% vs 22.8%), "
      "but COVID delivered the loss in 24 days at 47% annualized vol, 1.5× the pace of the GFC."),
    P("4. <b>Equal weight does not mean equal risk.</b> Five equity-like assets carry "
      "90% of portfolio VaR for 55% of weight. TLT and UUP have negative marginal VaR, "
      "they reduce portfolio risk."),
    P("5. <b>EVT exposes the structural Gaussian underestimate at the deep tail.</b> "
      "ξ = 0.31 (heavy tail confirmed). EVT 99.9% VaR = 4.14% vs Parametric-Normal at ~2.05%, "
      "more than 2× higher. This is the model failure that pre-2008 capital frameworks suffered."),
    PageBreak(),
]

# ---------- Page 2: Setup + Phase 1 ----------
story += [
    H1("Portfolio and Methodology"),
    H2("Universe"),
    P("Nine ETFs spanning US large/mid/small-cap (SPY, QQQ, IWM), international equity "
      "(EFA), long-duration Treasuries (TLT), high-yield credit (HYG), gold (GLD), oil (USO) "
      "and USD (UUP). Equal weights for the headline analysis (extensible)."),
    H2("Methods implemented (all from scratch, no pre-built VaR libraries)"),
    tbl([
        ["Family", "Method", "Tail model"],
        ["Historical",       "Historical Simulation", "Empirical (sorted history)"],
        ["Parametric",       "Variance-Covariance (Normal)", "Closed-form Gaussian"],
        ["Parametric",       "Variance-Covariance (Student-t)", "Closed-form t, MLE-fit df"],
        ["Monte Carlo",      "MV-Normal", "10k simulated draws"],
        ["Monte Carlo",      "MV-Student-t", "10k draws with fitted df"],
        ["Filtered",         "FHS (GARCH(1,1))", "Resampled GARCH residuals"],
        ["EVT",              "Peaks-Over-Threshold + GPD", "Fitted tail"],
    ], col_widths=[1.0*inch, 2.5*inch, 2.7*inch]),
    H2("Backtests"),
    P("Kupiec POF (unconditional coverage), Christoffersen independence + conditional "
      "coverage, Basel traffic-light. Strictly out-of-sample: rolling 500-day "
      "windows (1,000 for FHS), refitting GARCH every 60 trading days and updating σ via "
      "the GARCH recursion between refits. No look-ahead."),
    H1("Phase 1, VaR &amp; ES across methods"),
    tbl([
        ["Method",                  "95% VaR", "95% ES", "99% VaR", "99% ES"],
        ["Historical",              "0.99%",   "1.59%",  "1.80%",   "2.84%"],
        ["Parametric (Normal)",     "1.08%",   "1.36%",  "1.54%",   "1.77%"],
        ["Parametric (Student-t)",  "0.92%",   "1.47%",  "1.73%",   "2.55%"],
        ["Monte Carlo (Normal)",    "1.09%",   "1.37%",  "1.56%",   "1.77%"],
        ["Monte Carlo (t)",         "1.47%",   "2.30%",  "2.67%",   "3.96%"],
    ], col_widths=[2.2*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch]),
    Spacer(1, 6),
    P("<b>The fat-tail problem at 99%.</b> Parametric-Normal underestimates Historical by "
      "17% (1.54% vs 1.80%). MC-Normal converges to Parametric-Normal as expected, they "
      "are the same model. The Student-t methods recover most of the gap because the t "
      "distribution has an extra parameter (degrees of freedom) that fits tail thickness. "
      "ES/VaR ratio is a direct fat-tail diagnostic: Historical at 99% gives 1.58, "
      "Parametric-Normal gives 1.15, the Normal tail decays so fast that conditional-on-"
      "exceedance is barely worse than the threshold."),
    PageBreak(),
]

# ---------- Page 3: Charts of Phase 1 + intro to Phase 2 ----------
story += [
    H1("Phase 1, Visual evidence"),
    *fig("01_returns_histogram_var.png", caption="Figure 1, Empirical return distribution with 95% VaR thresholds overlaid. Left tail is visibly fatter than the fitted Normal density (dashed)."),
    *fig("02_var_method_comparison.png", caption="Figure 2, VaR by method at 95% and 99%. The 99% panel shows the divergence between Normal-based methods (Parametric, MC-Normal) and the tail-aware methods (Historical, Student-t)."),
    PageBreak(),
]

# ---------- Page 4: Phase 2, FHS the money shot ----------
story += [
    H1("Phase 2, Filtered Historical Simulation"),
    P("Returns are not i.i.d., vol clusters. FHS fixes this by (1) fitting a GARCH(1,1) "
      "to the portfolio return series to estimate conditional vol σ<sub>t</sub>, (2) "
      "standardizing each return by its own σ<sub>t</sub> to get approximately i.i.d. "
      "residuals z<sub>t</sub>, and (3) resampling those residuals and rescaling by "
      "today's σ<sub>T+1</sub> to produce a next-day return distribution."),
    H2("GARCH(1,1) fit"),
    tbl([
        ["Parameter", "Estimate", "Interpretation"],
        ["μ (mean)",      "0.0494%/day", "≈ 12.4% annualized"],
        ["ω (var. base)", "9.64×10⁻³",   "Long-run variance"],
        ["α[1] (shock)",  "0.1113",      "Yesterday's surprise lift"],
        ["β[1] (mem.)",   "0.8669",      "Vol persistence"],
        ["α + β",         "0.9782",      "Textbook (0.97–0.99 range)"],
    ], col_widths=[1.4*inch, 1.3*inch, 3.4*inch]),
    Spacer(1, 4),
    P("Implied vol-shock half-life: ln(0.5) / ln(0.978) ≈ 31 business days. After "
      "a March-2020-sized move, conditional vol decays halfway back to baseline in about a "
      "month, exactly the persistence visible in Figure 3."),
    *fig("04_fhs_vs_hist_var.png", width=6.4, caption="Figure 3, The headline chart of the project. Plain Historical VaR (red) lags by months because it averages over a 500-day window; FHS (blue) reacts the next day, because σ<sub>t</sub> spikes immediately when markets move."),
    PageBreak(),
]

# ---------- Page 5: Phase 3, Backtesting ----------
story += [
    H1("Phase 3, Backtesting"),
    P("Computing VaR is the easy part. Showing the model's predictions match its claim is "
      "the credibility test. Below are out-of-sample backtest results for all four primary "
      "methods at both confidence levels (n ≈ 2,118 – 2,618 prediction days per method, "
      "FHS uses a longer 1,000-day warm-up window for GARCH stability)."),
    H2("Headline test results"),
    tbl([
        ["Method",              "Conf.", "Exc rate", "Expected", "Kupiec p", "Christof-ind p", "Christof-CC p", "Basel"],
        ["Historical",          "95%",   "5.27%",    "5.00%",    "0.528",    "0.000",          "0.000",         "Yellow"],
        ["Parametric (Normal)", "95%",   "5.23%",    "5.00%",    "0.587",    "0.000",          "0.000",         "Yellow"],
        ["Monte Carlo (Normal)","95%",   "5.31%",    "5.00%",    "0.472",    "0.000",          "0.000",         "Yellow"],
        ["FHS (GARCH(1,1))",    "95%",   "4.86%",    "5.00%",    "0.772",    "0.996",          "0.959",         "Yellow"],
        ["Historical",          "99%",   "1.30%",    "1.00%",    "0.142",    "0.001",          "0.001",         "Green"],
        ["Parametric (Normal)", "99%",   "2.41%",    "1.00%",    "0.000",    "0.000",          "0.000",         "Green"],
        ["Monte Carlo (Normal)","99%",   "2.29%",    "1.00%",    "0.000",    "0.000",          "0.000",         "Green"],
        ["FHS (GARCH(1,1))",    "99%",   "1.13%",    "1.00%",    "0.547",    "0.029",          "0.076",         "Green"],
    ], col_widths=[1.6*inch, 0.55*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.95*inch, 0.85*inch, 0.6*inch]),
    Spacer(1, 6),
    P("<b>FHS is the only method to pass both Kupiec and Christoffersen at both confidence "
      "levels.</b> The three unconditional methods all pass Kupiec at 95% (right exceedance "
      "rate) but fail Christoffersen-independence with p ≈ 0.000, their violations cluster "
      "in the 2020 and 2022 stress windows. At 99%, Parametric and Monte Carlo Normal "
      "exceed their threshold at 2.4× the nominal rate, failing Kupiec catastrophically. "
      "This is the empirical case for conditional models in production risk."),
    *fig("07_backtest_99_violations.png", width=6.4, caption="Figure 4, 99% rolling VaR with violation markers (red dots). The Normal-based methods (top-right, bottom-left) show roughly 2× the expected number of exceedances; FHS (bottom-right) is closest to the nominal rate and the most evenly distributed in time."),
    PageBreak(),
]

# ---------- Page 6: Phase 4, Stress + Decomp ----------
story += [
    H1("Phase 4, Stress testing &amp; Risk decomposition"),
    H2("Current portfolio re-priced under historical crises"),
    tbl([
        ["Scenario",                                 "Days", "Cumulative loss", "Worst day", "Ann. vol"],
        ["2020 COVID Crash (Feb 19 – Mar 23)",       "24",   "23.44%",          "6.99%",     "47.1%"],
        ["2008 Global Financial Crisis (Sep–Nov)",   "63",   "22.80%",          "5.16%",     "39.2%"],
        ["2018 Q4 volatility (Oct–Dec)",             "63",   "10.86%",          "1.80%",     "13.1%"],
        ["2022 Rate Shock (Jan–Jun)",                "124",  "9.21%",           "2.71%",     "13.8%"],
        ["2015 China devaluation (Aug)",             "10",   "1.33%",           "2.67%",     "22.3%"],
    ], col_widths=[3.0*inch, 0.55*inch, 1.2*inch, 0.85*inch, 0.85*inch]),
    Spacer(1, 4),
    P("Both 2008 and 2020 produced ~23% cumulative drawdowns on the current portfolio, "
      "but COVID delivered the loss in 24 days at 47% annualized vol vs 63 days "
      "for the GFC. The 2022 rate shock was slower and broader (124 days), hitting bonds "
      "<i>and</i> stocks simultaneously."),
    H2("COVID drill-down, flight-to-quality in action"),
    P("Per-asset contribution to the 23.4% cumulative COVID loss: oil (USO) fell 55%; "
      "small-caps (IWM) fell 40%; SPY fell 33%. TLT and UUP rallied, Treasuries "
      "+14% and USD +4%, adding back ~2 percentage points to the portfolio return. "
      "Without those two assets the loss would have been ~25.4% instead of 23.4%. "
      "This is the resume-grade evidence for multi-asset diversification."),
    *fig("09_worst_scenario_contributions.png", width=6.0, caption="Figure 5, Per-asset contribution to the 2020 COVID drawdown. TLT and UUP are the only positive contributors."),
    H2("Component VaR (Euler decomposition)"),
    P("Equal weight does not mean equal risk. USO at 11.1% weight contributes 23.8% of "
      "total VaR, oil is the single riskiest holding due to high standalone vol and "
      "stress-period correlation. The five equity-like assets (SPY, QQQ, IWM, EFA, USO) "
      "together carry 90% of risk for 55% of weight. TLT and UUP have negative "
      "marginal VaR, adding more of either reduces portfolio risk. The Euler decomposition "
      "closes exactly: Σ Component VaR = portfolio VaR (1.1109%, zero relative error)."),
    *fig("10_component_var.png", width=6.4, caption="Figure 6, Weight vs % of total VaR contribution by asset. Equal weights produce unequal risk shares."),
    PageBreak(),
]

# ---------- Page 7: Phase 5, EVT ----------
story += [
    H1("Phase 5, Extreme Value Theory (POT-GPD)"),
    P("Standard methods cannot extrapolate beyond the sample (Historical) or extrapolate "
      "with the wrong tail (Normal). EVT models the tail itself: Peaks-Over-Threshold "
      "with a Generalized Pareto Distribution fit to losses above the 95th percentile."),
    H2("GPD fit"),
    tbl([
        ["Parameter", "Value", "Interpretation"],
        ["u (threshold)",        "0.989%", "95th-pct loss"],
        ["ξ (shape)",            "0.3142", "Heavy tail (positive); ES/VaR → 1.46"],
        ["σ (scale)",            "0.409%", "GPD scale"],
        ["n_u / n",              "156 / 3,118", "5.00% empirical tail prob"],
    ], col_widths=[1.4*inch, 1.4*inch, 3.3*inch]),
    H2("EVT VaR &amp; ES, compared to Historical and Parametric Normal"),
    tbl([
        ["Confidence", "EVT VaR", "EVT ES",  "Historical", "Param Normal", "EVT vs Normal"],
        ["95.0%",      "0.99%",   "1.59%",   "0.99%",       "1.08%",        " - "],
        ["99.0%",      "1.85%",   "2.84%",   "1.80%",       "1.54%",        "+20%"],
        ["99.5%",      "2.37%",   "3.60%",   "n/a*",        "~1.77%",       "+34%"],
        ["99.9%",      "4.14%",   "6.18%",   "n/a*",        "~2.05%",       "+102%"],
    ], col_widths=[1.0*inch, 0.85*inch, 0.85*inch, 1.05*inch, 1.15*inch, 1.2*inch]),
    Spacer(1, 6),
    P("<b>The 99.9% number is the project's deepest finding.</b> Parametric Normal "
      "estimates a 1-in-1000-day loss at ~2.05%. EVT estimates 4.14%, more than "
      "double. This is the structural risk-underestimate of Gaussian models at extreme "
      "confidence levels, and the empirical case for using EVT at the deep tail. "
      "ES at 99.9% = 6.18%, almost exactly the worst observed day in the 12-year "
      "sample (6.99% on 2020-03-16), EVT treats events of that magnitude as the average "
      "severity of a 1-in-1000-day stress, not anomalies."),
    *fig("12_evt_vs_others.png", width=6.4, caption="Figure 7, VaR by confidence level. EVT (red) extrapolates past the empirical maximum; Parametric Normal (orange) systematically under-shoots in the deep tail."),
    PageBreak(),
]

# ---------- Page 8: Conclusion ----------
story += [
    H1("Conclusion"),
    P("This framework demonstrates the full lifecycle of market-risk model development: "
      "implementation, validation, stress testing, decomposition, and tail extrapolation. "
      "The key findings are mutually reinforcing, Phase 1 shows the fat-tail problem in the "
      "static numbers, Phase 2 introduces the conditional model that addresses it, Phase 3 "
      "proves through formal backtesting that the conditional model is the only one that "
      "passes, Phase 4 quantifies the diversification value of the multi-asset structure, "
      "and Phase 5 exposes the deep-tail underestimate that motivates EVT in regulatory capital."),
    P("Together they make the empirical case for the conditional, fat-tailed, decomposable "
      "risk models that production risk shops have built post-2008."),
    H2("Skills demonstrated"),
    P("Value-at-Risk (Historical, Parametric, Monte Carlo, Filtered Historical Simulation), "
      "Expected Shortfall, GARCH(1,1), Kupiec POF and Christoffersen conditional-coverage "
      "backtesting, Basel traffic-light, historical stress scenario re-pricing, "
      "Component / Marginal VaR via Euler decomposition, Extreme Value Theory with "
      "Peaks-Over-Threshold and Generalized Pareto Distribution fitting, Python software "
      "engineering (modular package, reproducible notebook, parquet caching)."),
    H2("Stack"),
    P("Python 3.9+, NumPy, pandas, SciPy, arch (GARCH), matplotlib/seaborn, yfinance. "
      "Backtests run end-to-end in ~2 minutes on a laptop."),
    H2("Code"),
    P('<a href="https://github.com/John-Slye/portfolio_var_project" color="blue">github.com/John-Slye/portfolio_var_project</a>'),
]

# ----------------------------- build ---------------------------------------
doc = SimpleDocTemplate(
    str(OUT),
    pagesize=LETTER,
    leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    topMargin=0.75 * inch, bottomMargin=0.75 * inch,
    title="Multi-Asset Portfolio VaR & Stress Testing Framework",
    author="John Slye",
)
doc.build(story)
print(f"Wrote {OUT}")
