import matplotlib.pyplot as plt
import nflreadpy as nfl
import polars as pl
import seaborn as sns
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import requests
from io import BytesIO

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

#initialize EPA
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
#merge epa with team name and logo
epa = epa.merge(
    teams[["team_abbr", "team_logo_espn"]],
    left_on="team",
    right_on="team_abbr",
    how="left"
)
#make team colors a variable
team_colors = dict(
    zip(
        teams["team_abbr"],
        teams["team_color"]
    )
)

plt.figure(figsize=(10,8))

#make bar plot
ax = sns.barplot(
    data=epa,
    x="epa_per_carry_change",
    y="team",
    hue="team",
    palette=team_colors,
    legend=False
)
#put logos
for i, row in enumerate(epa.itertuples()):

    response = requests.get(row.team_logo_espn)
    img = Image.open(BytesIO(response.content)).convert("RGBA")

    img = img.resize((50, 50), Image.Resampling.LANCZOS)

    imagebox = OffsetImage(img, zoom=0.35)

    if row.epa_per_carry_change >= 0:
        offset = 5
        alignment = (0, 0.5)
    else:
        offset = -5
        alignment = (1, 0.5)

    ab = AnnotationBbox(
        imagebox,
        (row.epa_per_carry_change, i),
        frameon=False,
        box_alignment=alignment,
        xybox=(offset, 0),
        xycoords="data",
        boxcoords="offset points"
    )

    ax.add_artist(ab)

#set graph settings
plt.title("EPA per Carry Improvement From 2025 to 2026")
plt.xlabel("Change in EPA per Carry")
plt.ylabel("Teams")
plt.tight_layout()


plt.savefig(
    "Graphs/rushing_epa_improvement.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()