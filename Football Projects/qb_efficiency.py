import matplotlib.pyplot as plt
import nflreadpy as nfl
import polars as pl
import numpy as np
from adjustText import adjust_text

#load all current stats
player_stats = (
    nfl.load_player_stats(
        2026,
        summary_level="reg"
    )
    .filter(pl.col("position") == "QB")
)

#sort top 40 players in passing attempts
eff = (
    player_stats
    .sort("attempts", descending=True)
    .select(["player_display_name", "position", "attempts", "passing_tds", "passing_interceptions"])
    .head(40)
    .to_pandas()
)

#set size of figure
plt.figure(figsize=[12, 8])

#initialize scatter plot
scatter = plt.scatter(
    eff["attempts"],
    eff["passing_tds"],
    c=eff["passing_interceptions"],
    cmap="RdYlGn_r",
    edgecolors="black"
)

# add interceptions color bar
plt.colorbar(scatter, label="Interceptions")

x = eff["attempts"]
y = eff["passing_tds"]

m, b = np.polyfit(x, y, 1)

x_sorted = np.sort(x)

#add trend line
plt.plot(
x_sorted,
    m*x_sorted + b,
    color="blue",
    linestyle="--",
    linewidth=2,
    label="Trend Line"
)

texts = []

#add player names
for _, row in eff.iterrows():
    texts.append(
        plt.text(
            row["attempts"],
            row["passing_tds"],
            row["player_display_name"],
            fontsize=8
        )
    )

#adjust player names so they aren't on top of each other
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

#put labels
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