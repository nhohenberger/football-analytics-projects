import matplotlib.pyplot as plt
import nflreadpy as nfl
import polars as pl
import seaborn as sns
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import requests
from io import BytesIO
#initialize nextgen stats
next_gen = nfl.load_nextgen_stats(
    seasons=2026
)

teams = nfl.load_teams()

#initialize data set needed
depth = (
    next_gen
    .filter((pl.col("player_position") == "QB") & (pl.col("attempts") >= 50))
    .join(teams, left_on='team_abbr', right_on='team_abbr', how='inner')
    .group_by(["player_display_name", "team_abbr", "team_color", "team_logo_espn"])
    .agg(pl.col("avg_intended_air_yards").mean())
    .sort("avg_intended_air_yards", descending=True)
    .select(["player_display_name", "avg_intended_air_yards", "team_logo_espn", "team_abbr", "team_color"])
    .to_pandas()
)



plt.figure(figsize=(10,8))

#make bar plot
ax = sns.barplot(
    data=depth,
    x="avg_intended_air_yards",
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
        (row.avg_intended_air_yards, i),
        frameon=False,
        box_alignment=alignment,
        xybox=(offset, 0),
        xycoords="data",
        boxcoords="offset points"
    )

    ax.add_artist(ab)


plt.xlabel('Average Depth of Target')
plt.ylabel('Player')
plt.title("QBs Average Depth of Target (Min 50 Pass Attempts)")

plt.tight_layout()


plt.savefig(
    "Graphs/avg_depth_target.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()
