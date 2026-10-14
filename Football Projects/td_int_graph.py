import matplotlib.pyplot as plt
import nflreadpy as nfl

#load player stats
player_stats = nfl.load_player_stats(
    2025,
    summary_level="reg"
)

#get top ten passing td leadesr from 2025
td_int = (
    player_stats
    .sort("passing_tds", descending=True)
    .select(["player_display_name", "position", "passing_tds", "passing_interceptions"])
    .head(10)
    .to_pandas()
)

#set graph size
plt.figure(figsize=(12, 8))


#initialize scatter plot
plt.scatter(
    td_int["passing_interceptions"],
    td_int["passing_tds"],
)

#add player names
for _, row in td_int.iterrows():
    plt.annotate(
        row["player_display_name"],
        (row["passing_interceptions"], row["passing_tds"]),
        fontsize=12,
    )

#add labels
plt.xlabel("Interceptions")
plt.ylabel("TDs")
plt.title("2025 TD-INT Ratio")

plt.show()

