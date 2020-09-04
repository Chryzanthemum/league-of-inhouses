import pandas as pd
from gspread_pandas import Spread, Client, conf
from trueskill import Rating, rate

spread = Spread('1tkX0iQF1tkrBSNVaEd4nAlisFt3AlwWGG0VrG8_OMPw')

players_df = spread.sheet_to_df(index=0, sheet='players')
teams_df = spread.sheet_to_df(index=0, sheet='teams')
outcomes_df = spread.sheet_to_df(index=0, sheet='game_record')

# only calculate based off of real games
outcomes_df = outcomes_df[outcomes_df['for_real']=='1']
teams_df = teams_df.merge(outcomes_df, how='inner')

player_ratings = {}
for match in teams_df['game_id'].unique():
    match_df = teams_df[teams_df['game_id']==match]
    # this feels really dumb but for each match, I need to know who was on what team and to maintain order
    ratings_1 = list()
    ratings_2 = list()
    team_1 = list()
    team_2 = list()
    for player in match_df['player_id']:
        if player not in player_ratings:
            player_ratings[player] = Rating()
        if match_df[match_df['player_id'] == player]['outcome'].values[0] == '1':
            ratings_1.append(player_ratings[player])
            team_1.append(player)
        else:
            ratings_2.append(player_ratings[player])
            team_2.append(player)
    
    new_r1, new_r2 = rate([ratings_1, ratings_2], ranks=[0, 1])
    
    for i in range(0,5):
        player_ratings[team_1[i]] = new_r1[i]
        player_ratings[team_2[i]] = new_r2[i]
        
elos_df = pd.DataFrame.from_dict(player_ratings, orient='index', columns=['mu', 'sigma']).reset_index().rename(columns={"index":"player_id"})

output_df = (
    teams_df
    .groupby(['player_id'])
    .agg({"game_id":"nunique"})
    .reset_index()
    .merge(elos_df)
    .merge(players_df)
    .rename(columns={"game_id":"games_played", "mu":"elo", "sigma":"elo_variance"})
    .loc[:,['name', 'ign', 'elo', 'elo_variance','games_played']]
    .sort_values('elo', ascending=False)
)

spread.df_to_sheet(df=output_df, sheet='stats')
