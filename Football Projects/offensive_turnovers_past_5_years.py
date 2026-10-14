import nflreadpy as nfl
import polars as pl

#initialize team stats
five_seasons =  [2022,2023,2024,2025,2026]
team_stats = nfl.load_team_stats(
    seasons=five_seasons,
    summary_level="reg+post"
)

trn = (
    team_stats
    .with_columns(
        (
            pl.col("passing_interceptions")
                + pl.col("sack_fumbles_lost")
                + pl.col("rushing_fumbles_lost")
                + pl.col("receiving_fumbles_lost")
         ) #add interceptions and fumbles
        .alias("game_turnovers") #name that game_turnovers
    )
    .group_by("team")
    .agg(
        pl.col("game_turnovers").sum().alias("total_offensive_turnovers_committed")
    )
    .sort("total_offensive_turnovers_committed", descending=True)
    .select(["team", "total_offensive_turnovers_committed"])
    .head(32)
    .to_pandas()
)

#make a bar graph next