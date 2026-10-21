import nflreadpy as nfl
import polars as pl
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import seaborn as sns
from PIL import Image
import requests
from io import BytesIO
charting = nfl.load_ftn_charting()
pbp = nfl.load_pbp(
    seasons=2026
)
players = nfl.load_players()
teams = nfl.load_teams()
team_meta = teams.select([
    "team_abbr",
    "team_color",
    "team_logo_espn"
])

pbp_drops = (
    pbp
    .filter(
        (pl.col("pass_attempt") == 1)
        & (pl.col("receiver_player_id").is_not_null())
    )
    .select([
        pl.col("play_id").cast(pl.Int64).alias("nflverse_play_id"),
        pl.col("receiver_player_id").alias("dropper"),
        pl.col("posteam").alias("team_abbr")
    ])
)



drops = (
    charting
    .select([
        pl.col("nflverse_play_id").cast(pl.Int64),
        "is_drop"
    ])
    .join(
        pbp_drops,
        on="nflverse_play_id",
        how="inner"
    )
    .group_by("dropper")
    .agg([
        pl.col("is_drop")
        .cast(pl.Int32)
        .sum()
        .alias("drops"),

        pl.col("team_abbr")
        .first()
        .alias("team_abbr")
    ])
    .join(
        players.select([
            "gsis_id",
            "display_name"
        ]),
        left_on="dropper",
        right_on="gsis_id",
        how="inner"
    )
    .join(
        team_meta,
        on="team_abbr",
        how="inner"
    )
    .filter(pl.col("drops") >= 4)
    .sort("drops", descending=True)
    .to_pandas()
)

plt.figure(figsize=(16, 12))

ax = sns.barplot(
    data=drops,
    x="drops",
    y="display_name",
    hue="display_name",
    palette=drops["team_color"].tolist(),
    legend=False
)

for i, row in enumerate(drops.itertuples()):
    try:
        response = requests.get(row.team_logo_espn, timeout=5)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        img = img.resize((50, 50), Image.Resampling.LANCZOS)
        imagebox = OffsetImage(img, zoom=0.30)

        offset = 5
        alignment = (0, 0.5)

        ab = AnnotationBbox(
            imagebox,
            (row.drops, i),
            frameon=False,
            box_alignment=alignment,
            xybox=(offset, 0),
            xycoords="data",
            boxcoords="offset points",
        )
        ax.add_artist(ab)
    except Exception as e:
        print(f"Could not load logo for {row.player_display_name}: {e}")

plt.xlabel("Number of Drops")
plt.ylabel("Player")
plt.title("2026 Number of Drops (min 4 drops)")

plt.tight_layout()

plt.savefig(
    "Graphs/num_of_drops",
    dpi=300,
    bbox_inches="tight"
)
plt.show()