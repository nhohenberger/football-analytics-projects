import matplotlib.pyplot as plt
import nflreadpy as nfl
import polars as pl
import seaborn as sns
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import requests
from io import BytesIO
import os
#initialize charting stats
charting = nfl.load_ftn_charting(
    seasons=2026
)

players = nfl.load_players()
teams = nfl.load_teams()
#get team abbreviation, color, and logo
team_meta = (
    teams
    .select(
        [
            pl.col("team_abbr"),
            pl.col("team_color").alias("team_color"),
            pl.col("team_logo_espn").alias("team_logo_espn")
        ]
    )
)

#initialize data set needed
depth = (
    charting
    .filter(
        (pl.col("passer_player_id").is_not_null()) &
        (pl.col("sacks_suffered") > 0)
    )
    .group_by("passer_player_id")
    .agg([
        pl.col("sacks_suffered").sum().alias("total_sacks"),
        # Cast boolean to integer so we can sum the QB-fault sacks
        pl.col("is_qb_fault_sack").cast(pl.Int32).sum().alias("qb_fault_sacks"),
        pl.col("team_abbr").first().alias("team_abbr")
    ])
    .join(
        players.select(["gsis_id", "player_display_name"]),
        left_on="passer_player_id",
        right_on="gsis_id",
        how="inner"
    )
    .join(
        players.select([pl.col("gsis_id"), pl.col("player_display_name")]),
        left_on="passer_player_id",
        right_on="gsis_id",
        how="inner"
    )
    # Join with our clean team metadata for colors and logos
    .join(team_meta, on="team_abbr", how="inner")
    # Sort by the most QB-fault sacks
    .sort("qb_fault_sacks", descending=True)
    .to_pandas()
)



plt.figure(figsize=(10,8))

#make bar plot
ax = sns.barplot(
    data=depth,
    x="qb_fault_sacks",
    y="player_display_name",
    hue="player_display_name",
    palette=depth["team_color"].tolist(),
    legend=False
)
#put logos
for i, row in enumerate(depth.itertuples()):

    response = requests.get(row.team_logo_espn, timeout=5)
    img = Image.open(BytesIO(response.content)).convert("RGBA")

    img = img.resize((50, 50), Image.Resampling.LANCZOS)

    imagebox = OffsetImage(img, zoom=0.30)


    offset = 5
    alignment = (0, 0.5)


    ab = AnnotationBbox(
        imagebox,
        (row.qb_fault_sacks, i),
        frameon=False,
        box_alignment=alignment,
        xybox=(offset, 0),
        xycoords="data",
        boxcoords="offset points"
    )

    ax.add_artist(ab)


plt.xlabel('Number of Sacks That Were the QBs Fault')
plt.ylabel('Player')
plt.title("Number of Sacks That Were the QBs Fault (Min One Time Sacked) ")

plt.tight_layout()


plt.savefig(
    "Graphs/qb_fault_sacks.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()
