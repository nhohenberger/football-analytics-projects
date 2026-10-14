#this is my first nfl program
import nflreadpy as nfl

#load player stats
player_stats = nfl.load_player_stats()

#sort players by passing yards with their name and yards
passing_yd_leaders = (
    player_stats
    .sort("passing_yards", descending=True)
    .select(["player_display_name", "passing_yards"])
    .head(10)
)

#sort players by passing tds with their name and tds
passing_td_leaders = (
    player_stats
    .sort("passing_tds", descending=True)
    .select(["player_display_name", "passing_tds"])
    .head(10)
)

#sort players by rushing yards with their name and yards
rushing_yd_leaders = (
    player_stats
    .sort("rushing_yards", descending=True)
    .select(["player_display_name", "rushing_yards"])
    .head(10)
)

#sort players by rushing tds with their name and tds
rushing_td_leaders = (
    player_stats
    .sort("rushing_tds", descending=True)
    .select(["player_display_name", "rushing_tds"])
    .head(10)
)

#print all tables
print(passing_yd_leaders)
print(passing_td_leaders)
print(rushing_yd_leaders)
print(rushing_td_leaders)