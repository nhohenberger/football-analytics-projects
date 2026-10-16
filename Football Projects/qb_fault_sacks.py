import matplotlib.pyplot as plt
import nflreadpy as nfl
import polars as pl
import seaborn as sns
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import requests
from io import BytesIO
import os

# 1. Initialize data loaders
season_year = 2026
charting = nfl.load_ftn_charting(seasons=season_year)
pbp = nfl.load_pbp(seasons=season_year)  # Load play-by-play to get players/sacks
players = nfl.load_players()
teams = nfl.load_teams()

# Clean team metadata
team_meta = teams.select([
    pl.col("team_abbr"),
    pl.col("team_color"),
    pl.col("team_logo_espn")
])

# 2. Extract sacks and quarterback IDs from main play-by-play
pbp_sacks = (
    pbp
    .filter((pl.col("sack") == 1) & (pl.col("passer_player_id").is_not_null()))
    .select([
        pl.col("play_id").cast(pl.Int64).alias("nflverse_play_id"),
        pl.col("passer_player_id"),
        # FIX: Map 'posteam' from pbp to 'team_abbr'
        pl.col("posteam").alias("team_abbr")
    ])
)

# 3. Join play-by-play data with FTN charting details
depth = (
    charting
    .select([
        pl.col("nflverse_play_id").cast(pl.Int64),
        pl.col("is_qb_fault_sack")
    ])
    .join(pbp_sacks, on="nflverse_play_id", how="inner")
    .group_by("passer_player_id")
    .agg([
        pl.len().alias("total_sacks"),
        pl.col("is_qb_fault_sack").cast(pl.Int32).sum().alias("qb_fault_sacks"),
        pl.col("team_abbr").first().alias("team_abbr")
    ])
    .join(
        players.select(["gsis_id", "display_name"]),
        left_on="passer_player_id",
        right_on="gsis_id",
        how="inner"
    )
    .join(team_meta, on="team_abbr", how="inner")
    .sort("qb_fault_sacks", descending=True)
    .to_pandas()
)

# 4. Plot configuration
plt.figure(figsize=(10, 8))

ax = sns.barplot(
    data=depth,
    x="qb_fault_sacks",
    y="display_name",
    hue="display_name",
    palette=depth["team_color"].tolist(),
    legend=False
)

# 5. Place logos
for i, row in enumerate(depth.itertuples()):
    try:
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
    except Exception as e:
        print(f"Could not load logo for {row.player_display_name}: {e}")

plt.xlabel("Number of Sacks That Were the QB's Fault")
plt.ylabel('Player')
plt.title(f"Number of Sacks That Were the QB's Fault ({season_year} Season)")

plt.tight_layout()

os.makedirs("Graphs", exist_ok=True)
plt.savefig(
    "Graphs/qb_fault_sacks.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()
