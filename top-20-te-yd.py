import matplotlib.pyplot as plt
import nflreadpy as nfl
import polars as pl
from adjustText import adjust_text

#import player stats
player_stats = (
    nfl.load_player_stats(
        seasons=True,
        summary_level="reg+post"
    )
)

players = nfl.load_players()

#initialize top 20 te's in receiving yards
te = (
    player_stats
    .filter(pl.col("position") == "TE")
    .group_by(["player_id", "player_display_name"])
    .agg(
        pl.col("receiving_yards").sum().alias("total_receiving_yards"),
        pl.col("receptions").sum().alias("total_receptions")
    )
    .join(players, left_on="player_id", right_on="gsis_id", how="left")
    .sort("total_receiving_yards", descending=True)
    .select(["player_display_name", "total_receptions", "total_receiving_yards"])
    .head(20)
    .to_pandas()
)

# set figure size
plt.figure(figsize=(12, 8))

scatter = plt.scatter(
    te["total_receiving_yards"],
    te["total_receptions"],
)

#put player text
texts = []
for _, row in te.iterrows():
    texts.append(
        plt.text(
            row["total_receiving_yards"],
            row["total_receptions"],
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

plt.xlabel("Receiving Yards")
plt.ylabel("Receptions")
plt.title("All time TE Receiving Yard Leaders (reg + post)")

plt.tight_layout()
plt.show()

