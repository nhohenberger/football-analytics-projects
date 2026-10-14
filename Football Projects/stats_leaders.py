#this is my first nfl program
import nflreadpy as nfl

player_stats = nfl.load_player_stats()

passing_yd_leaders = (
    player_stats
    .sort("passing_yards", descending=True)
    .select(["player_display_name", "passing_yards"])
    .head(10)
)

passing_td_leaders = (
    player_stats
    .sort("passing_tds", descending=True)
    .select(["player_display_name", "passing_tds"])
    .head(10)
)

rushing_yd_leaders = (
    player_stats
    .sort("rushing_yards", descending=True)
    .select(["player_display_name", "rushing_yards"])
    .head(10)
)

rushing_td_leaders = (
    player_stats
    .sort("rushing_tds", descending=True)
    .select(["player_display_name", "rushing_tds"])
    .head(10)
)

print(passing_yd_leaders)
print(passing_td_leaders)
print(rushing_yd_leaders)
print(rushing_td_leaders)