#this code is AI because i asked it to switch something for me and i didnt figure out what it changed
import io
import urllib.request
import matplotlib.pyplot as plt
import nflreadpy as nfl
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from adjustText import adjust_text
import polars as pl
from PIL import Image

# -----------------------
# Load Data
# -----------------------

season_year = 2026

charting = nfl.load_ftn_charting(seasons=season_year)
pbp = nfl.load_pbp(seasons=season_year)
players = nfl.load_players()
teams = nfl.load_teams()

team_meta = teams.select([
    "team_abbr",
    "team_color",
    "team_logo_espn"
])

# -----------------------
# Passing Attempts
# -----------------------

pbp_attempts = (
    pbp
    .filter(
        (pl.col("pass_attempt") == 1)
        & (pl.col("passer_player_id").is_not_null())
    )
    .select([
        pl.col("play_id").cast(pl.Int64).alias("nflverse_play_id"),
        pl.col("passer_player_id"),
        pl.col("posteam").alias("team_abbr")
    ])
)

# -----------------------
# QB Metrics
# -----------------------

catchable = (
    charting
    .select([
        pl.col("nflverse_play_id").cast(pl.Int64),
        "is_catchable_ball",
        "is_interception_worthy"
    ])
    .join(
        pbp_attempts,
        on="nflverse_play_id",
        how="inner"
    )
    .group_by("passer_player_id")
    .agg([
        pl.len().alias("attempts"),

        pl.col("is_catchable_ball")
        .cast(pl.Int32)
        .sum()
        .alias("catchable"),

        pl.col("is_interception_worthy")
        .cast(pl.Int32)
        .sum()
        .alias("interceptable"),

        pl.col("team_abbr")
        .first()
        .alias("team_abbr")
    ])
    .with_columns([
        (
            pl.col("catchable")
            / pl.col("attempts")
            * 100
        ).alias("catchable_pct"),

        (
            pl.col("interceptable")
            / pl.col("attempts")
            * 100
        ).alias("interceptable_pct")
    ])
    .join(
        players.select([
            "gsis_id",
            "display_name"
        ]),
        left_on="passer_player_id",
        right_on="gsis_id",
        how="inner"
    )
    .join(
        team_meta,
        on="team_abbr",
        how="inner"
    )
    .filter(pl.col("attempts") >= 150)
    .sort("catchable_pct", descending=True)
    .to_pandas()
)

# -----------------------
# Plot Setup
# -----------------------

plt.rcParams["figure.dpi"] = 300

fig, ax = plt.subplots(figsize=(16, 10))

ax.scatter(
    catchable["interceptable_pct"],
    catchable["catchable_pct"],
    alpha=0
)


x_pad = (
    catchable["interceptable_pct"].max()
    - catchable["interceptable_pct"].min()
) * 0.15

y_pad = (
    catchable["catchable_pct"].max()
    - catchable["catchable_pct"].min()
) * 0.15

ax.set_xlim(
    catchable["interceptable_pct"].min() - x_pad,
    catchable["interceptable_pct"].max() + x_pad
)
ax.invert_xaxis()

ax.set_ylim(
    catchable["catchable_pct"].min() - y_pad,
    catchable["catchable_pct"].max() + y_pad
)

# -----------------------
# Logo Helper
# -----------------------

def get_logo(url):

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(req) as response:
        image_data = response.read()

    img = Image.open(io.BytesIO(image_data))

    img = img.resize(
        (50, 50),
        Image.LANCZOS
    )

    return img


# -----------------------
# Logos + Labels
# -----------------------

texts = []

for _, row in catchable.iterrows():

    try:

        logo_img = get_logo(
            row["team_logo_espn"]
        )

        imagebox = OffsetImage(
            logo_img,
            zoom=0.50
        )

        ab = AnnotationBbox(
            imagebox,
            (
                row["interceptable_pct"],
                row["catchable_pct"]
            ),
            frameon=False
        )

        ax.add_artist(ab)

        x_off = 0.03
        y_off = 0.03

        if row["display_name"] == "Patrick Mahomes":
            x_off = -0.10
            y_off = 0.00

        text = ax.text(
            row["interceptable_pct"] + x_off,
            row["catchable_pct"] + y_off,
            row["display_name"],
            fontsize=9,
            weight="bold"
        )

        texts.append(text)

    except Exception as e:

        print(
            f"Could not load logo for "
            f"{row['display_name']}: {e}"
        )

# -----------------------
# Prevent Label Overlap
# -----------------------

adjust_text(
    texts,
    ax=ax,
    expand_points=(1.1, 1.1),
    expand_text=(1.1, 1.1),
    force_points=0.15,
    force_text=0.15,
    arrowprops=dict(
        arrowstyle="-",
        color="gray",
        alpha=0.5,
        lw=0.6
    )
)

# -----------------------
# League Average Lines
# -----------------------

league_avg_interceptable = (
    catchable["interceptable_pct"].mean()
)

league_avg_catchable = (
    catchable["catchable_pct"].mean()
)

ax.axvline(
    league_avg_interceptable,
    color="red",
    linestyle="--",
    linewidth=1.5,
    alpha=0.8
)

ax.axhline(
    league_avg_catchable,
    color="red",
    linestyle="--",
    linewidth=1.5,
    alpha=0.8
)

# -----------------------
# Grid
# -----------------------

ax.grid(
    linestyle="--",
    alpha=0.3
)

# -----------------------
# Titles
# -----------------------

ax.set_xlabel(
    "Interceptable Ball Rate (%)",
    fontsize=12
)

ax.set_ylabel(
    "Catchable Ball Rate (%)",
    fontsize=12
)

ax.set_title(
    f"{season_year} QB Accuracy vs Turnover-Worthy Throw Rate\n(Minimum 150 Attempts)",
    fontsize=16,
    fontweight="bold"
)

plt.tight_layout()
plt.savefig(
    "Graphs/turnover_worthy_throw.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()