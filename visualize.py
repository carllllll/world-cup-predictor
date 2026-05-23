import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from simulator import run_tournament

def plot_winner_odds():
    results = run_tournament(10000)
    top15 = dict(list(results.items())[:15])

    teams = list(top15.keys())
    probs = list(top15.values())

    colors = []
    for p in probs:
        if p >= 12:
            colors.append("#FFD700")   # gold - top favorites
        elif p >= 6:
            colors.append("#FF6B35")   # orange - contenders
        elif p >= 2:
            colors.append("#4ECDC4")   # teal - dark horses
        else:
            colors.append("#95A5A6")   # grey - longshots

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor("#0D1B2A")
    ax.set_facecolor("#0D1B2A")

    bars = ax.barh(teams[::-1], probs[::-1], color=colors[::-1],
                   edgecolor="white", linewidth=0.4, height=0.6)

    for bar, prob in zip(bars, probs[::-1]):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                f"{prob}%", va="center", ha="left",
                color="white", fontsize=10, fontweight="bold")

    ax.set_xlabel("Win Probability (%)", color="white", fontsize=11)
    ax.set_title("🏆 2026 FIFA World Cup — Winner Probabilities\n(10,000 simulations)",
                 color="white", fontsize=14, fontweight="bold", pad=15)

    ax.tick_params(colors="white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#333")
    ax.spines["bottom"].set_color("#333")
    ax.xaxis.label.set_color("white")

    legend_elements = [
        mpatches.Patch(color="#FFD700", label="Top Favorites (12%+)"),
        mpatches.Patch(color="#FF6B35", label="Contenders (6–12%)"),
        mpatches.Patch(color="#4ECDC4", label="Dark Horses (2–6%)"),
        mpatches.Patch(color="#95A5A6", label="Longshots (<2%)"),
    ]
    ax.legend(handles=legend_elements, loc="lower right",
              facecolor="#1a2a3a", labelcolor="white", fontsize=9)

    plt.tight_layout()
    plt.savefig("world_cup_odds.png", dpi=150, bbox_inches="tight",
                facecolor="#0D1B2A")
    plt.show()
    print("Chart saved as world_cup_odds.png")

if __name__ == "__main__":
    plot_winner_odds()