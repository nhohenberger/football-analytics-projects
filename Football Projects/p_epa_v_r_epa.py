import io
import urllib.request
import matplotlib.pyplot as plt
import nflreadpy as nfl
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import numpy as np
from PIL import Image

#load team stats
team_stats = nfl.load_team_stats(
    seasons=[2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
    summary_level="reg+post"
).to_pandas()
#load teams
teams = nfl.load_teams().to_pandas()

#initialize epas
epas = (
    team_stats
    .groupby("team")[["passing_epa", "rushing_epa"]]
    .mean()
    .reset_index()
)

#merge with team abbr and logo
epas = epas.merge(
    teams[["team_abbr", "team_logo_espn"]],
    left_on="team",
    right_on="team_abbr"
)

#create scatter plot
fig, ax = plt.subplots(figsize=(12, 8))

#establish x and y axis
ax.scatter(epas["passing_epa"], epas["rushing_epa"], alpha=0)

#initialize x and y
x = epas["passing_epa"]
y = epas["rushing_epa"]

#set slope and y-intercept of trend line
m, b = np.polyfit(x, y, 1)

x_sorted = np.sort(x)

#plot trend line
plt.plot(
    x_sorted,
    m*x_sorted + b,
    color="blue",
    linestyle="--",
    linewidth=2,
    label="Trend Line"
)

#helper function to get the logo
def get_logo(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        image_data = response.read()
    img = Image.open(io.BytesIO(image_data))

    img = img.resize((60, 60), Image.LANCZOS)
    return img



# plot each logo
for _, row in epas.iterrows():
    try:
        # Fetch the logo from the ESPN CDN URL provided by nflreadpy
        logo_img = get_logo(row["team_logo_espn"])

        # Control logo size with the 'zoom' parameter (adjust based on preference)
        imagebox = OffsetImage(logo_img, zoom=0.6)

        # Map the logo to the exact (x, y) coordinates
        ab = AnnotationBbox(
            imagebox,
            (row["passing_epa"], row["rushing_epa"]),
            frameon=False,  # Hides borders around the logo
        )
        ax.add_artist(ab)
    except Exception as e:
        # Fallback if a URL fails to load
        print(f"Could not load logo for {row['team']}: {e}")

#set graph settings
ax.set_xlabel("Passing EPA per Play")
ax.set_ylabel("Rushing EPA per Play")
ax.set_title("2018-2025 Team Efficiency (Passing vs Rushing)", fontsize=16, fontweight="bold")
ax.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig(
    "Graphs/epa_graphMAHOMES.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()