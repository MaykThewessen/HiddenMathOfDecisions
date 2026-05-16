"""Generate additional charts for the Readme: sunk cost and decision system overview."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

output_dir = Path("charts")
output_dir.mkdir(exist_ok=True)
plt.style.use("seaborn-v0_8-whitegrid")
colors = {"blue": "#2F5496", "green": "#375623", "red": "#C00000",
          "orange": "#ED7D31", "gold": "#FFC000", "gray": "#666666", "light_gray": "#E0E0E0"}

# --- Sunk Cost: Forward-looking decision matrix ---
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: What people think matters
sunk_amounts = [15, 5000, 50000, 200000]
labels = ["Movie\nticket", "Job\n(1 year)", "Relationship\n(3 years)", "Business\n(5 years)"]
bars = axes[0].barh(labels, sunk_amounts, color=colors["red"], alpha=0.7)
axes[0].set_xlabel("Amount Already Invested ($)")
axes[0].set_title("What People Focus On\n(IRRELEVANT)", fontsize=12, fontweight="bold", color=colors["red"])
for bar, val in zip(bars, sunk_amounts):
    axes[0].text(bar.get_width() + max(sunk_amounts) * 0.02, bar.get_y() + bar.get_height() / 2,
                 f"${val:,}", va="center", fontweight="bold", fontsize=10)
axes[0].set_xlim(0, max(sunk_amounts) * 1.3)

# Right: What actually matters
future_continue = [-5, 30000, -20000, 50000]
future_quit = [10, 80000, 40000, 120000]
x = np.arange(len(labels))
width = 0.35
b1 = axes[1].barh(x - width / 2, future_continue, width, label="Future value: CONTINUE", color=colors["orange"])
b2 = axes[1].barh(x + width / 2, future_quit, width, label="Future value: QUIT", color=colors["green"])
axes[1].set_yticks(x)
axes[1].set_yticklabels(labels)
axes[1].set_xlabel("Future Value ($)")
axes[1].set_title("What Actually Matters\n(ONLY forward-looking value)", fontsize=12, fontweight="bold", color=colors["green"])
axes[1].legend(fontsize=9, loc="lower right")
axes[1].axvline(x=0, color=colors["gray"], linestyle="-", alpha=0.3)

fig.suptitle("Sunk Cost Fallacy: Past Investment vs Future Value", fontsize=14, fontweight="bold", y=1.02)
fig.tight_layout()
fig.savefig(output_dir / "3_sunk_cost.svg", bbox_inches="tight")
plt.close(fig)

# --- Decision System Overview (flowchart-style) ---
fig, ax = plt.subplots(figsize=(14, 6))
ax.set_xlim(0, 14)
ax.set_ylim(0, 6)
ax.axis("off")

steps = [
    (1.5, 3, "1. Expected\nValue", "Should I act?", "#2F5496"),
    (3.8, 3, "2. Base\nRates", "What's the real\nprobability?", "#375623"),
    (6.1, 3, "3. Sunk\nCosts", "What should\nI ignore?", "#C00000"),
    (8.4, 3, "4. Bayes", "How do I\nupdate?", "#ED7D31"),
    (10.7, 3, "5. Survivorship\nBias", "What am I\nNOT seeing?", "#7030A0"),
    (13.0, 3, "6. Kelly\nCriterion", "How much to\ncommit?", "#00B050"),
]

for x_pos, y_pos, title, subtitle, color in steps:
    box = mpatches.FancyBboxPatch(
        (x_pos - 0.95, y_pos - 0.8), 1.9, 1.6,
        boxstyle="round,pad=0.15", facecolor=color, edgecolor="white",
        linewidth=2, alpha=0.9
    )
    ax.add_patch(box)
    ax.text(x_pos, y_pos + 0.15, title, ha="center", va="center",
            fontsize=10, fontweight="bold", color="white")
    ax.text(x_pos, y_pos - 0.55, subtitle, ha="center", va="center",
            fontsize=8, color="white", alpha=0.9)

# Arrows between boxes
for i in range(len(steps) - 1):
    ax.annotate("", xy=(steps[i + 1][0] - 1.0, steps[i + 1][1]),
                xytext=(steps[i][0] + 1.0, steps[i][1]),
                arrowprops=dict(arrowstyle="->", color=colors["gray"], lw=2))

# Title and subtitle
ax.text(7, 5.3, "The Complete Decision System", ha="center", va="center",
        fontsize=16, fontweight="bold", color=colors["blue"])
ax.text(7, 4.7, "Run through all 6 before any major decision", ha="center", va="center",
        fontsize=11, color=colors["gray"], style="italic")

# Bottom: decision output
output_box = mpatches.FancyBboxPatch(
    (4.5, 0.3), 5, 0.9,
    boxstyle="round,pad=0.15", facecolor=colors["gold"], edgecolor=colors["orange"],
    linewidth=2
)
ax.add_patch(output_box)
ax.text(7, 0.75, "DECISION: Act with calculated confidence", ha="center", va="center",
        fontsize=12, fontweight="bold", color="#333333")

# Arrow from last box down to output
ax.annotate("", xy=(7, 1.2), xytext=(7, 2.2),
            arrowprops=dict(arrowstyle="->", color=colors["gray"], lw=2))

fig.savefig(output_dir / "7_decision_system.svg", bbox_inches="tight")
plt.close(fig)

print("Extra charts saved:")
print("  charts/3_sunk_cost.svg")
print("  charts/7_decision_system.svg")
