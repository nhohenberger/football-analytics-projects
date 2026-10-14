import matplotlib.pyplot as plt
import nflreadpy as nfl
import polars as pl
import numpy as np
from adjustText import adjust_text

player_stats = (
    nfl.load_player_stats(
        2026,
        summary_level="reg"
    )
    .filter(pl.col("position") == "QB")
)

eff = (
    player_stats
    .sort("attempts", descending=True)
    .select(["player_display_name", "position", "attempts", "passing_tds", "passing_interceptions"])
    .head(40)
    .to_pandas()
)

plt.figure(figsize=[12, 8])

scatter = plt.scatter(
    eff["attempts"],
    eff["passing_tds"],
    c=eff["passing_interceptions"],
    cmap="RdYlGn_r",
    edgecolors="black"
)

plt.colorbar(scatter, label="Interceptions")

x = eff["attempts"]
y = eff["passing_tds"]

m, b = np.polyfit(x, y, 1)

x_sorted = np.sort(x)

plt.plot(
x_sorted,
    m*x_sorted + b,
    color="blue",
    linestyle="--",
    linewidth=2,
    label="Trend Line"
)

texts = []

for _, row in eff.iterrows():
    texts.append(
        plt.text(
            row["attempts"],
            row["passing_tds"],
            row["player_display_name"],
            fontsize=8
        )
    )

adjust_text(
    texts,
    expand_points=(2.5, 2.5),
    expand_text=(2.5, 2.5),
    force_points=1.5,
    force_text=1.5,
    arrowprops=dict(
        arrowstyle="-",
        color="gray",
        lw=0.5
    )
)

plt.xlabel("Passing attempts")
plt.ylabel("Passing TDs")
plt.title("Top 40 QBs: Passing TDs vs Attempts (Color = INTs)")

plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(
    "Graphs/qb_efficiency.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()