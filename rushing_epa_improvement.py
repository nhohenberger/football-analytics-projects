import matplotlib.pyplot as plt
import nflreadpy as nfl
import polars as pl
import pandas as pd
import seaborn as sns
#initialize team stats
team_stats = nfl.load_team_stats(
    seasons=[2025,2026],
    summary_level="reg+post"
)
#initialize teams
teams = nfl.load_teams().to_pandas()

epa_pivoted = team_stats.pivot(
    on="season",
    index="team",
    values=["rushing_epa", "carries"]
)

epa = (
    epa_pivoted
    .with_columns(
        (
            pl.col("rushing_epa_2026") /
            pl.col("carries_2026")
        ).alias("epa_per_carry_2026"),

        (
            pl.col("rushing_epa_2025") /
            pl.col("carries_2025")
        ).alias("epa_per_carry_2025")
    )
    .with_columns(
        (
            pl.col("epa_per_carry_2026") -
            pl.col("epa_per_carry_2025")
        ).alias("epa_per_carry_change")
    )
    .select([
        "team",
        "epa_per_carry_2025",
        "epa_per_carry_2026",
        "epa_per_carry_change"
    ])
    .sort("epa_per_carry_change", descending=True)
    .to_pandas()
)

plt.figure(figsize=(10,8))
sns.barplot(
    data=epa,
    x='epa_per_carry_change',
    y='team',
    palette=teams["team_color"].tolist(),
    hue='team',
    legend=False
)

#set graph settings
plt.title("EPA per Carry Improvement")
plt.xlabel("EPA per Carry")
plt.ylabel("Teams")
plt.tight_layout()


plt.show()