"""
The Hidden Math Behind Every Decision You Make
================================================
Interactive Python implementations of the 6 mental models,
with optional matplotlib visualizations.

Usage:
    python decision_math.py              # text-only demo
    python decision_math.py --plot       # demo + save charts to PNG

Or import individual functions:
    from decision_math import expected_value, bayes_update, kelly_criterion
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np


# ---------------------------------------------------------------------------
# 1. Expected Value
# ---------------------------------------------------------------------------

def expected_value(outcomes: list[tuple[float, float]]) -> float:
    """
    Calculate expected value from a list of (probability, payoff) tuples.

    >>> expected_value([(0.5, 150), (0.5, -100)])
    25.0
    """
    return sum(p * v for p, v in outcomes)


def simulate_ev(outcomes: list[tuple[float, float]], n_trials: int = 10_000,
                rng: np.random.Generator | None = None) -> np.ndarray:
    """Monte Carlo simulation of cumulative returns over n_trials."""
    if rng is None:
        rng = np.random.default_rng(42)
    probs, payoffs = zip(*outcomes)
    draws = rng.choice(payoffs, size=n_trials, p=probs)
    return np.cumsum(draws)


# ---------------------------------------------------------------------------
# 2. Base Rate Neglect
# ---------------------------------------------------------------------------

def base_rate_correction(
    base_rate: float,
    sensitivity: float,
    false_positive_rate: float,
) -> float:
    """
    Calculate true probability given a positive test result (Bayes' theorem).

    >>> round(base_rate_correction(0.001, 0.99, 0.01), 4)
    0.0902
    """
    true_pos = sensitivity * base_rate
    false_pos = false_positive_rate * (1 - base_rate)
    return true_pos / (true_pos + false_pos)


def base_rate_sweep(sensitivity: float = 0.99, fpr: float = 0.01,
                    n_points: int = 200) -> tuple[np.ndarray, np.ndarray]:
    """Show how P(sick|positive) changes across different base rates."""
    base_rates = np.linspace(0.0001, 0.10, n_points)
    posteriors = np.array([base_rate_correction(br, sensitivity, fpr) for br in base_rates])
    return base_rates, posteriors


# ---------------------------------------------------------------------------
# 3. Sunk Cost Fallacy
# ---------------------------------------------------------------------------

def sunk_cost_check(
    already_invested: float,
    future_cost_to_continue: float,
    future_value_if_continue: float,
    future_value_if_quit: float,
) -> dict:
    """
    Evaluate whether to continue or quit, ignoring sunk costs.
    Only compares FUTURE costs and benefits.
    """
    net_continue = future_value_if_continue - future_cost_to_continue
    net_quit = future_value_if_quit

    return {
        "already_invested (irrelevant)": already_invested,
        "net_value_if_continue": net_continue,
        "net_value_if_quit": net_quit,
        "recommendation": "CONTINUE" if net_continue > net_quit else "QUIT",
        "difference": abs(net_continue - net_quit),
    }


# ---------------------------------------------------------------------------
# 4. Bayesian Thinking
# ---------------------------------------------------------------------------

def bayes_update(
    prior: float,
    likelihood_if_true: float,
    likelihood_if_false: float,
) -> float:
    """
    Update a belief using Bayes' theorem.

    >>> round(bayes_update(0.10, 0.70, 0.15), 4)
    0.3415
    """
    numerator = likelihood_if_true * prior
    denominator = numerator + likelihood_if_false * (1 - prior)
    return numerator / denominator


def bayes_chain(prior: float,
                evidence: list[tuple[float, float]]) -> list[float]:
    """
    Chain multiple Bayesian updates. Returns list of posteriors
    including the prior as the first element.

    Args:
        prior: initial belief
        evidence: list of (likelihood_if_true, likelihood_if_false)
    """
    posteriors = [prior]
    current = prior
    for lt, lf in evidence:
        current = bayes_update(current, lt, lf)
        posteriors.append(current)
    return posteriors


# ---------------------------------------------------------------------------
# 5. Survivorship Bias
# ---------------------------------------------------------------------------

def survivorship_bias_adjusted(
    visible_successes: int,
    estimated_total_attempts: int,
) -> dict:
    """Estimate the real success rate by accounting for invisible failures."""
    real_rate = visible_successes / estimated_total_attempts
    failures = estimated_total_attempts - visible_successes
    return {
        "visible_successes": visible_successes,
        "estimated_total_attempts": estimated_total_attempts,
        "invisible_failures": failures,
        "real_success_rate": real_rate,
        "real_success_pct": f"{real_rate:.2%}",
    }


# ---------------------------------------------------------------------------
# 6. Kelly Criterion
# ---------------------------------------------------------------------------

def kelly_criterion(
    win_prob: float,
    win_multiplier: float,
    fraction: float = 1.0,
) -> dict:
    """
    Calculate optimal bet size using the Kelly Criterion.

    >>> kelly_criterion(0.60, 1.0)['full_kelly']
    0.2
    """
    q = 1 - win_prob
    full_kelly = (win_prob * win_multiplier - q) / win_multiplier
    full_kelly = max(0, full_kelly)

    return {
        "full_kelly": round(full_kelly, 4),
        "recommended_bet": round(full_kelly * fraction, 4),
        "fraction_used": fraction,
        "edge": round(win_prob * win_multiplier - q, 4),
    }


def kelly_growth_simulation(
    win_prob: float = 0.60,
    win_mult: float = 1.0,
    n_bets: int = 300,
    n_paths: int = 50,
    rng: np.random.Generator | None = None,
) -> dict[str, np.ndarray]:
    """
    Simulate bankroll growth under Full, Half, and Quarter Kelly
    to show how aggressive sizing increases volatility.
    """
    if rng is None:
        rng = np.random.default_rng(42)

    q = 1 - win_prob
    full_k = max(0, (win_prob * win_mult - q) / win_mult)
    fractions = {"Full Kelly": full_k, "Half Kelly": full_k / 2, "Quarter Kelly": full_k / 4}

    results = {}
    wins = rng.random((n_paths, n_bets)) < win_prob

    for label, f in fractions.items():
        bankrolls = np.ones((n_paths, n_bets + 1))
        for t in range(n_bets):
            bet = bankrolls[:, t] * f
            gain = np.where(wins[:, t], bet * win_mult, -bet)
            bankrolls[:, t + 1] = bankrolls[:, t] + gain
        results[label] = bankrolls

    return results


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def create_plots(output_dir: Path) -> None:
    """Generate all visualizations and save to output_dir."""
    import matplotlib.pyplot as plt

    output_dir.mkdir(exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    colors = {"blue": "#2F5496", "green": "#375623", "red": "#C00000",
              "orange": "#ED7D31", "gold": "#FFC000", "gray": "#666666"}

    # --- Figure 1: Monte Carlo EV simulation ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Coin flip
    cum = simulate_ev([(0.5, 150), (0.5, -100)], n_trials=500)
    axes[0].plot(cum, color=colors["blue"], linewidth=1.5)
    axes[0].axhline(y=0, color=colors["gray"], linestyle="--", alpha=0.5)
    ev_line = np.arange(1, 501) * 25
    axes[0].plot(ev_line, color=colors["red"], linestyle="--", linewidth=1, label="EV = $25/flip")
    axes[0].set_title("Coin Flip: Cumulative Returns (500 flips)", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Flip #")
    axes[0].set_ylabel("Cumulative Profit ($)")
    axes[0].legend()

    # Career choice — multiple simulations
    rng = np.random.default_rng(42)
    for i in range(20):
        cum_b = simulate_ev([(0.60, 250_000), (0.40, 70_000)], n_trials=10, rng=rng)
        axes[1].plot(cum_b, color=colors["blue"], alpha=0.3, linewidth=1)
    # Add EV line
    ev_career = np.arange(1, 11) * 178_000
    axes[1].plot(ev_career, color=colors["red"], linestyle="--", linewidth=2, label="EV = $178K/period")
    axes[1].axhline(y=120_000 * np.arange(1, 11)[-1], color=colors["green"], linestyle=":",
                     linewidth=2, label="Safe job total")
    axes[1].set_title("Career Choice: 20 Simulated Paths", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Period")
    axes[1].set_ylabel("Cumulative Earnings ($)")
    axes[1].legend(fontsize=9)

    fig.tight_layout()
    fig.savefig(output_dir / "1_expected_value.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- Figure 2: Base Rate Sweep ---
    fig, ax = plt.subplots(figsize=(8, 5))
    base_rates, posteriors = base_rate_sweep()
    ax.plot(base_rates * 100, posteriors * 100, color=colors["blue"], linewidth=2)
    ax.axhline(y=99, color=colors["red"], linestyle="--", alpha=0.7, label="What people guess (99%)")
    ax.axvline(x=0.1, color=colors["orange"], linestyle=":", alpha=0.7, label="1 in 1,000 prevalence")
    ax.scatter([0.1], [base_rate_correction(0.001, 0.99, 0.01) * 100],
               color=colors["red"], s=100, zorder=5)
    ax.annotate(f"  Actual: {base_rate_correction(0.001, 0.99, 0.01):.1%}",
                xy=(0.1, base_rate_correction(0.001, 0.99, 0.01) * 100),
                fontsize=11, fontweight="bold", color=colors["red"])
    ax.set_xlabel("Base Rate (prevalence %)", fontsize=11)
    ax.set_ylabel("P(actually sick | positive test) %", fontsize=11)
    ax.set_title("How Base Rate Affects Your True Probability", fontsize=12, fontweight="bold")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "2_base_rate.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- Figure 3: Bayesian Update Progression ---
    fig, ax = plt.subplots(figsize=(8, 5))
    evidence = [(0.70, 0.15), (0.60, 0.10), (0.80, 0.20)]
    labels = ["Prior", "LinkedIn\nupdate", "Outside\ncalls", "Vague on\nprojects"]
    posteriors = bayes_chain(0.10, evidence)

    ax.plot(range(len(posteriors)), [p * 100 for p in posteriors],
            marker="o", markersize=10, linewidth=2.5, color=colors["blue"])
    for i, p in enumerate(posteriors):
        ax.annotate(f"{p:.0%}", xy=(i, p * 100), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=11, fontweight="bold",
                    color=colors["blue"])
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("P(coworker is quitting) %", fontsize=11)
    ax.set_title("Bayesian Belief Update: Is She Quitting?", fontsize=12, fontweight="bold")
    ax.set_ylim(0, 100)
    ax.axhline(y=50, color=colors["gray"], linestyle="--", alpha=0.4, label="50/50 threshold")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "4_bayesian_update.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- Figure 4: Survivorship Bias ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # What you see vs reality
    categories = ["Crypto\nTwitter", "Spotify\nTracks", "Restaurants\n(5yr)"]
    visible = [50, 10, 200]
    invisible = [450, 89990, 800]

    x = np.arange(len(categories))
    width = 0.35
    axes[0].bar(x - width / 2, visible, width, label="Visible (winners)", color=colors["green"])
    axes[0].bar(x + width / 2, invisible, width, label="Invisible (losers)", color=colors["red"], alpha=0.7)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(categories)
    axes[0].set_ylabel("Count")
    axes[0].set_title("What You See vs Reality", fontsize=12, fontweight="bold")
    axes[0].legend()
    axes[0].set_yscale("log")

    # Success rates
    rates = [r / (r + i) * 100 for r, i in zip(visible, invisible)]
    bars = axes[1].bar(categories, rates, color=[colors["blue"], colors["orange"], colors["red"]])
    for bar, rate in zip(bars, rates):
        axes[1].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                     f"{rate:.2f}%", ha="center", fontweight="bold", fontsize=10)
    axes[1].set_ylabel("Real Success Rate (%)")
    axes[1].set_title("Actual Success Rates (Log Scale Winners)", fontsize=12, fontweight="bold")

    fig.tight_layout()
    fig.savefig(output_dir / "5_survivorship_bias.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- Figure 5: Kelly Criterion Growth Curves ---
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    results = kelly_growth_simulation()

    for ax, (label, bankrolls) in zip(axes, results.items()):
        color = {"Full Kelly": colors["red"], "Half Kelly": colors["orange"],
                 "Quarter Kelly": colors["green"]}[label]
        median = np.median(bankrolls, axis=0)
        for path in bankrolls[:20]:
            ax.plot(path, color=color, alpha=0.15, linewidth=0.8)
        ax.plot(median, color=color, linewidth=2.5, label=f"Median ({label})")
        ax.axhline(y=1, color=colors["gray"], linestyle="--", alpha=0.3)
        ax.set_title(label, fontsize=12, fontweight="bold")
        ax.set_xlabel("Bet #")
        ax.legend(fontsize=9)

    axes[0].set_ylabel("Bankroll (starting = 1.0)")
    fig.suptitle("Kelly Criterion: Aggressive vs Conservative Sizing (60% edge, 1:1 payout)",
                 fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(output_dir / "6_kelly_growth.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"  Charts saved to {output_dir}/")


# ---------------------------------------------------------------------------
# Interactive demo
# ---------------------------------------------------------------------------

def _separator(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def main():
    parser = argparse.ArgumentParser(description="Decision Math — 6 Mental Models")
    parser.add_argument("--plot", action="store_true", help="Generate matplotlib charts")
    parser.add_argument("--output", type=str, default="charts", help="Output directory for charts")
    args = parser.parse_args()

    # --- 1. Expected Value ---
    _separator("1. EXPECTED VALUE")

    print("Coin flip bet: Heads -> +$150, Tails -> -$100")
    ev = expected_value([(0.5, 150), (0.5, -100)])
    print(f"  EV = ${ev:+.2f} per flip")
    print(f"  Over 100 flips: ~${ev * 100:+,.0f}\n")

    print("Career choice:")
    ev_a = expected_value([(1.0, 120_000)])
    ev_b = expected_value([(0.60, 250_000), (0.40, 70_000)])
    print(f"  Option A (safe job):    EV = ${ev_a:,.0f}")
    print(f"  Option B (startup):     EV = ${ev_b:,.0f}")
    print(f"  Difference:             ${ev_b - ev_a:+,.0f}")

    # --- 2. Base Rate Neglect ---
    _separator("2. BASE RATE NEGLECT")

    print("Disease test: 1/1000 prevalence, 99% accurate test")
    p = base_rate_correction(0.001, 0.99, 0.01)
    print(f"  P(actually sick | positive test) = {p:.1%}")
    print(f"  NOT 99% -- only {p:.1%}!\n")

    print("Startup unicorn odds:")
    p2 = base_rate_correction(0.00006, 0.80, 0.05)
    print(f"  Even with strong signals, P(unicorn) = {p2:.4%}")

    # --- 3. Sunk Cost ---
    _separator("3. SUNK COST FALLACY")

    print("Bad movie: paid $15, 30 min in, it's terrible.")
    result = sunk_cost_check(
        already_invested=15,
        future_cost_to_continue=0,
        future_value_if_continue=-5,
        future_value_if_quit=10,
    )
    print(f"  Sunk cost ($15): IRRELEVANT to the decision")
    print(f"  Future value if stay:  {result['net_value_if_continue']}")
    print(f"  Future value if leave: {result['net_value_if_quit']}")
    print(f"  -> {result['recommendation']}")

    # --- 4. Bayesian Updating ---
    _separator("4. BAYESIAN THINKING")

    print("Is your coworker about to quit?")
    evidence = [(0.70, 0.15), (0.60, 0.10), (0.80, 0.20)]
    labels = ["Prior", "After LinkedIn update", "After outside calls", "After vague on projects"]
    posteriors = bayes_chain(0.10, evidence)
    for label, p in zip(labels, posteriors):
        bar = "#" * int(p * 40)
        print(f"  {label:28s} {p:5.0%}  |{bar}")

    # --- 5. Survivorship Bias ---
    _separator("5. SURVIVORSHIP BIAS")

    print("Crypto Twitter gains posts:")
    result = survivorship_bias_adjusted(visible_successes=50, estimated_total_attempts=500)
    print(f"  You see {result['visible_successes']} success stories")
    print(f"  But {result['invisible_failures']} failures are invisible")
    print(f"  Real success rate: {result['real_success_pct']}\n")

    print("Spotify 'go viral' advice:")
    result2 = survivorship_bias_adjusted(visible_successes=10, estimated_total_attempts=90_000)
    print(f"  Daily uploads: {result2['estimated_total_attempts']:,}")
    print(f"  Viral tracks: ~{result2['visible_successes']}")
    print(f"  Real rate: {result2['real_success_pct']}")

    # --- 6. Kelly Criterion ---
    _separator("6. KELLY CRITERION")

    print("Bet with 60% win probability, 1:1 payout:")
    k = kelly_criterion(0.60, 1.0)
    print(f"  Full Kelly:    {k['full_kelly']:.0%} of bankroll")
    print(f"  Edge:          {k['edge']:.0%}\n")

    print("Practical sizing (bankroll = $10,000):")
    bankroll = 10_000
    for frac, label in [(1.0, "Full Kelly"), (0.5, "Half Kelly"), (0.25, "Quarter Kelly")]:
        k = kelly_criterion(0.60, 1.0, fraction=frac)
        print(f"  {label:15s}: bet {k['recommended_bet']:.0%} = ${k['recommended_bet'] * bankroll:,.0f}")

    # --- Summary ---
    _separator("THE COMPLETE DECISION SYSTEM")
    print("  1. EV           -> Should I act?")
    print("  2. Base Rates   -> What's the real probability?")
    print("  3. Sunk Costs   -> What should I ignore?")
    print("  4. Bayes        -> How do I update my beliefs?")
    print("  5. Survivorship -> What am I NOT seeing?")
    print("  6. Kelly        -> How much should I commit?")
    print()

    # --- Charts ---
    if args.plot:
        _separator("GENERATING CHARTS")
        output_dir = Path(args.output)
        create_plots(output_dir)
        print(f"\n  5 chart files saved to ./{output_dir}/")


if __name__ == "__main__":
    main()
