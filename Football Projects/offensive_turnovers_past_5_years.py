import matplotlib.pyplot as plt
import nflreadpy as nfl
import polars as pl
import seaborn as sns


#initialize team stats
five_seasons =  [2022,2023,2024,2025,2026]
team_stats = nfl.load_team_stats(
    seasons=five_seasons,
    summary_level="reg+post"
)
#load teams
teams = nfl.load_teams()

#initialize turnovers
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
    .join(teams, left_on="team", right_on="team_abbr", how="left")
    .sort("total_offensive_turnovers_committed", descending=True)
    .select(["team", "total_offensive_turnovers_committed", "team_color"])
    .head(32)
    .to_pandas()
)
#set size
plt.figure(figsize = (10,8))
#initialize bar graph
sns.barplot(
    data=trn,
    x='total_offensive_turnovers_committed',
    y='team',
    palette=trn["team_color"].tolist(),
    hue='team',
    legend=False
)

#set graph settings
plt.title("NFL Teams Offensive Turnovers Since 2022")
plt.xlabel("Total Offensive Turnovers")
plt.ylabel("Teams")
plt.tight_layout()

plt.savefig(
    "Graphs/offensive_turnovers_last5.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()