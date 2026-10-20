import matplotlib.pyplot as plt
import nflreadpy as nfl
import polars as pl
import pandas as pd
import seaborn as sns
# from matplotlib.offsetbox import OffsetImage, AnnotationBbox
# from PIL import Image
# import requests
# from io import BytesIO
# import os

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

# 2. Extract attempts, and quarterback IDs from main play-by-play
pbp_attempts = (
    pbp
    .filter((pl.col("pass_attempt") == 1) & (pl.col("passer_player_id").is_not_null()))
    .select([
        pl.col("play_id").cast(pl.Int64).alias("nflverse_play_id"),
        pl.col("passer_player_id"),
        # FIX: Map 'posteam' from pbp to 'team_abbr'
        pl.col("posteam").alias("team_abbr"),

    ])
)

# 3. Join play-by-play data with FTN charting details
catchable = (
    charting
    .select([
        pl.col("nflverse_play_id").cast(pl.Int64),
        pl.col("pass_attempt"),
        pl.col("is_catchable_ball")
    ])
    .join(pbp_attempts, on="nflverse_play_id", how="inner")
    .group_by("passer_player_id")
    .agg([
        pl.len().alias("attempts"),
        pl.col("is_catchable_ball").cast(pl.Int32).sum().alias("catchable"),
        pl.col("team_abbr").first().alias("team_abbr")
    ])
    .join(
        players.select(["gsis_id", "display_name"]),
        left_on="passer_player_id",
        right_on="gsis_id",
        how="inner"
    )
    .join(team_meta, on="team_abbr", how="inner")
    .sort("catchable", descending=True)
    .to_pandas()
)

#4. make scatterplot

sns.scatterplot(
    data=catchable,
    x="attempts",
    y="catchable",
    hue="team_abbr",
    s=150,
    legend=False
)

for _, row in catchable.iterrows():
    plt.text(
        row['attempts'],
        row['catchable'],
        row["display_name"],
        fontsize=8
    )

plt.xlabel("Pass Attempts")
plt.ylabel("Catchable Balls")
plt.title("2026 QB Catchable Balls vs Attempts")

plt.show()