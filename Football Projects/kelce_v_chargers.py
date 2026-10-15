import matplotlib.pyplot as plt
import nflreadpy as nfl
import polars as pl
from adjustText import adjust_text
import requests
from PIL import Image
from io import BytesIO
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
#import player stats
player_stats = nfl.load_player_stats(
        seasons=True,
        summary_level="week"
    )
#load players
players = nfl.load_players()

#initialize kelce picture
kelce_url = (
    players
    .filter(pl.col("gsis_id") == "00-0030506")
    .select("headshot")
    .item()
)
response = requests.get(kelce_url)
img = Image.open(BytesIO(response.content))

#initialize travis kelce against chargers
te = (
    player_stats
    .filter(
        (pl.col("player_id") == "00-0030506") &
        (pl.col("opponent_team") == "LAC")
    )
    .sort("receiving_yards", descending=True)
    .select(["receptions", "receiving_yards", "week", "season", "headshot_url"])
    .to_pandas()
)

# set figure size
plt.figure(figsize=(12, 8))

scatter = plt.scatter(
    te["receiving_yards"],
    te["receptions"],
    color="#E31837",
    edgecolor="#FFB81C",
    s=100
)

#put line for kelce to break the record
plt.axvline(
    x=88,
    color="black",
    linestyle="--",
    linewidth=2,
    label="Yards Needed to Break Record"
)

#put week and season text
texts = []
for _, row in te.iterrows():

    texts.append(
        plt.text(
            row["receiving_yards"],
            row["receptions"],
            row["season"],
            fontsize=9,
            fontweight="bold"
        )
    )

#adjust week and player labels so they aren't on top of each other
adjust_text(
    texts,
    expand_points=(2.5, 2.5),
    expand_text=(2.5, 2.5),
    force_points=1.5,
    force_text=1.5,
    arrowprops=dict(
        arrowstyle="-",
        color="gray",
        lw=0.5
    )
)

plt.xlabel("Receiving Yards")
plt.ylabel("Receptions")
plt.title("Travis Kelce Versus Chargers")

imagebox = OffsetImage(
    img,
    zoom=0.05
)

#add image
ab = AnnotationBbox(
    imagebox,
    (0.1, 0.90),
    xycoords="axes fraction",
    frameon=False
)
plt.gca().add_artist(ab)

plt.tight_layout()
plt.savefig(
    "Graphs/kelce_v_chargers.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

