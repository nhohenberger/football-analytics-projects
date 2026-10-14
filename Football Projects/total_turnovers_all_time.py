import nflreadpy as nfl

team_stats = nfl.load_team_stats(
    seasons=True,
    summary_level="reg+post"
)

trn = (

)