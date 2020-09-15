import copy
import json
import requests
import pandas as pd
from gspread_pandas import Spread, Client, conf
from trueskill import Rating, rate


def trydict(key, value):
    print(key)
    try:
        return key[value]
    except:
        return np.nan


spread = Spread('1tkX0iQF1tkrBSNVaEd4nAlisFt3AlwWGG0VrG8_OMPw')

players_df = spread.sheet_to_df(index=0, sheet='players')
player_participants_df = spread.sheet_to_df(index=0, sheet='game_participant_ids').astype({"participant_id": int})
games_df = spread.sheet_to_df(index=0, sheet='game_ids')

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": "RGAPI-7b0e62ff-2714-43ad-93f3-48192cc06659"
}

champion_ids = {
    1: "Annie",
    2: "Olaf",
    3: "Galio",
    4: "TwistedFate",
    5: "XinZhao",
    6: "Urgot",
    7: "LeBlanc",
    8: "Vladimir",
    9: "Fiddlesticks",
    10: "Kayle",
    11: "Master Yi",
    12: "Alistar",
    13: "Ryze",
    14: "Sion",
    15: "Sivir",
    16: "Soraka",
    17: "Teemo",
    18: "Tristana",
    19: "Warwick",
    20: "Nunu",
    21: "MissFortune",
    22: "Ashe",
    23: "Tryndamere",
    24: "Jax",
    25: "Morgana",
    26: "Zilean",
    27: "Singed",
    28: "Evelynn",
    29: "Twitch",
    30: "Karthus",
    31: "Cho'Gath",
    32: "Amumu",
    33: "Rammus",
    34: "Anivia",
    35: "Shaco",
    36: "Dr.Mundo",
    37: "Sona",
    38: "Kassadin",
    39: "Irelia",
    40: "Janna",
    41: "Gangplank",
    42: "Corki",
    43: "Karma",
    44: "Taric",
    45: "Veigar",
    48: "Trundle",
    50: "Swain",
    51: "Caitlyn",
    53: "Blitzcrank",
    54: "Malphite",
    55: "Katarina",
    56: "Nocturne",
    57: "Maokai",
    58: "Renekton",
    59: "JarvanIV",
    60: "Elise",
    61: "Orianna",
    62: "Wukong",
    63: "Brand",
    64: "LeeSin",
    67: "Vayne",
    68: "Rumble",
    69: "Cassiopeia",
    72: "Skarner",
    74: "Heimerdinger",
    75: "Nasus",
    76: "Nidalee",
    77: "Udyr",
    78: "Poppy",
    79: "Gragas",
    80: "Pantheon",
    81: "Ezreal",
    82: "Mordekaiser",
    83: "Yorick",
    84: "Akali",
    85: "Kennen",
    86: "Garen",
    89: "Leona",
    90: "Malzahar",
    91: "Talon",
    92: "Riven",
    96: "Kog'Maw",
    98: "Shen",
    99: "Lux",
    101: "Xerath",
    102: "Shyvana",
    103: "Ahri",
    104: "Graves",
    105: "Fizz",
    106: "Volibear",
    107: "Rengar",
    110: "Varus",
    111: "Nautilus",
    112: "Viktor",
    113: "Sejuani",
    114: "Fiora",
    115: "Ziggs",
    117: "Lulu",
    119: "Draven",
    120: "Hecarim",
    121: "Kha'Zix",
    122: "Darius",
    126: "Jayce",
    127: "Lissandra",
    131: "Diana",
    133: "Quinn",
    134: "Syndra",
    136: "AurelionSol",
    141: "Kayn",
    142: "Zoe",
    143: "Zyra",
    145: "Kai'sa",
    150: "Gnar",
    154: "Zac",
    157: "Yasuo",
    161: "Vel'Koz",
    163: "Taliyah",
    164: "Camille",
    201: "Braum",
    202: "Jhin",
    203: "Kindred",
    222: "Jinx",
    223: "TahmKench",
    235: "Senna",
    236: "Lucian",
    238: "Zed",
    240: "Kled",
    245: "Ekko",
    246: "Qiyana",
    254: "Vi",
    266: "Aatrox",
    267: "Nami",
    268: "Azir",
    350: "Yuumi",
    412: "Thresh",
    420: "Illaoi",
    421: "Rek'Sai",
    427: "Ivern",
    429: "Kalista",
    432: "Bard",
    497: "Rakan",
    498: "Xayah",
    516: "Ornn",
    517: "Sylas",
    523: "Aphelios",
    518: "Neeko",
    555: "Pyke",
    777: "Yone",
    875: "Sett",
    876: "Lillia",
}

role_dict = {
    "BOTTOM/DUO_CARRY": "BOT",
    "JUNGLE/NONE": "JUNGLE",
    "TOP/SOLO": "TOP",
    "MIDDLE/SOLO": "MIDDLE",
    "TOP/DUO": "TOP",
    "MIDDLE/DUO": "MIDDLE",
    "BOTTOM/DUO_SUPPORT": "SUPPORT"
}

player_stats = list()
inhouse_counter = 0
for g in games_df['league_game_id']:
    r = requests.get(f'https://na1.api.riotgames.com/lol/match/v4/matches/{g}', headers=headers)
    for p in r.json()['participants']:
        try:
            cs_diff_per_min_deltas = p['timeline']['csDiffPerMinDeltas']
        except:
            cs_diff_per_min_deltas = np.nan

        try:
            xp_diff_per_min_deltas = p['timeline']['xpDiffPerMinDeltas']
        except:
            xp_diff_per_min_deltas = np.nan

        try:
            creeps_per_min_deltas = p['timeline']['creepsPerMinDeltas']
        except:
            creeps_per_min_deltas = np.nan
        player_stats.append([g,
                             p['participantId'],
                             inhouse_counter,
                             p['teamId'],
                             p['championId'],
                             r.json()['gameDuration'],
                             p['stats']['win'],
                             p['stats']['kills'],
                             p['stats']['deaths'],
                             p['stats']['assists'],
                             p['stats']['totalDamageDealtToChampions'],
                             p['stats']['totalDamageTaken'],
                             p['stats']['totalMinionsKilled'],
                             p['stats']['neutralMinionsKilled'],
                             p['timeline']['role'],
                             p['timeline']['lane'],
                             cs_diff_per_min_deltas,
                             xp_diff_per_min_deltas,
                             creeps_per_min_deltas
                             ])
    inhouse_counter += 1

player_stats_df = pd.DataFrame(player_stats,
                               columns=['game_id',
                                        'participant_id',
                                        'inhouse_id',
                                        'team_id',
                                        'champion_id',
                                        'game_duration',
                                        'win',
                                        'kills',
                                        'deaths',
                                        'assists',
                                        'total_damage_dealt_to_champs',
                                        'total_damage_taken',
                                        'minions_killed',
                                        'creeps_killed',
                                        'role',
                                        'lane',
                                        'cs_diff_per_min_delta',
                                        'xp_diff_per_min_delta',
                                        'creeps_per_min'
                                        ])

deltas = ['cs_diff_per_min_delta', 'xp_diff_per_min_delta', 'creeps_per_min']
for c in deltas:
    player_stats_df = player_stats_df.merge(
        player_stats_df[c]
        .apply(pd.Series)
        .rename(columns={"0-10": f'{c}_0-10', "10-20": f'{c}_10-20', "20-30": f'{c}_20-30'}),
        left_index=True,
        right_index=True
    )

player_stats_df = (
    player_stats_df
    .merge(player_participants_df)
    .merge(players_df)
    .assign(
        combined_role=lambda d: (d['lane'] + '/' + d['role']),
        champion=lambda d: d['champion_id'].map(champion_ids),
        win=lambda d: d['win'].astype(int),
        role=lambda d: d['combined_role'].map(role_dict)
    )
    .drop(columns=['champion_id', 'lane', '0_x', '0_y'])
)

spread.df_to_sheet(df=player_stats_df, sheet='player_stats')

post_game_ratings = list()
player_ratings = {}
counter = 0

players = player_stats_df['player_id'].unique()
for player in players:
    player_ratings[player] = Rating()

for match in player_stats_df['inhouse_id'].unique():
    match_df = player_stats_df[player_stats_df['inhouse_id'] == match]
    # this feels really dumb but for each match, I need to know who was on what team and to maintain order
    ratings_1 = list()
    ratings_2 = list()
    team_1 = list()
    team_2 = list()
    for player in match_df['player_id']:
        if match_df[match_df['player_id'] == player]['win'].values[0] == 1:
            ratings_1.append(player_ratings[player])
            team_1.append(player)
        else:
            ratings_2.append(player_ratings[player])
            team_2.append(player)

    new_r1, new_r2 = rate([ratings_1, ratings_2], ranks=[0, 1])

    for i in range(0, 5):
        player_ratings[team_1[i]] = new_r1[i]
        player_ratings[team_2[i]] = new_r2[i]

    for player in players:
        post_game_ratings.append([counter, player, player_ratings[player].sigma, player_ratings[player].mu])
    counter += 1


current_elos_df = pd.DataFrame.from_dict(player_ratings, orient='index', columns=[
                                         'mu', 'sigma']).reset_index().rename(columns={"index": "player_id"})

per_game_elo_df = pd.DataFrame(post_game_ratings, columns=['game_id', 'player_id', 'sigma', 'mu'])

output_df = (
    player_stats_df
    .groupby(['player_id'])
    .agg({"game_id": "nunique", "win": "sum"})
    .reset_index()
    .merge(current_elos_df)
    .merge(players_df)
    .rename(columns={"game_id": "games_played", "win": "games_won", "mu": "elo", "sigma": "elo_variance"})
    .loc[:, ['name', 'ign', 'elo', 'elo_variance', 'games_played', 'games_won']]
    .sort_values('elo', ascending=False)
)

output_df.head()

spread.df_to_sheet(df=output_df, sheet='stats')

spread.df_to_sheet(df=per_game_elo_df, sheet='elo_over_time')

post_game_ratings = list()
player_ratings = {}
counter = 0

players = player_stats_df['player_id'].unique()
for player in players:
    player_ratings[player] = Rating()

for match in player_stats_df['inhouse_id'].unique():
    match_df = player_stats_df[player_stats_df['inhouse_id'] == match]
    # this feels really dumb but for each match, I need to know who was on what team and to maintain order
    ratings_1 = list()
    ratings_2 = list()
    team_1 = list()
    team_2 = list()
    for player in match_df['player_id']:
        if match_df[match_df['player_id'] == player]['win'].values[0] == 1:
            ratings_1.append(player_ratings[player])
            team_1.append(player)
        else:
            ratings_2.append(player_ratings[player])
            team_2.append(player)

    new_r1, new_r2 = rate([ratings_1, ratings_2], ranks=[0, 1])

    for i in range(0, 5):
        player_ratings[team_1[i]] = new_r1[i]
        player_ratings[team_2[i]] = new_r2[i]

    for player in players:
        post_game_ratings.append([counter, player, player_ratings[player].sigma, player_ratings[player].mu])
    counter += 1


current_elos_df = pd.DataFrame.from_dict(player_ratings, orient='index', columns=[
                                         'mu', 'sigma']).reset_index().rename(columns={"index": "player_id"})

per_game_elo_df = pd.DataFrame(post_game_ratings, columns=['game_id', 'player_id', 'sigma', 'mu'])

output_df = (
    player_stats_df
    .groupby(['player_id'])
    .agg({"game_id": "nunique", "win": "sum"})
    .reset_index()
    .merge(current_elos_df)
    .merge(players_df)
    .rename(columns={"game_id": "games_played", "win": "games_won", "mu": "elo", "sigma": "elo_variance"})
    .loc[:, ['name', 'ign', 'elo', 'elo_variance', 'games_played', 'games_won']]
    .sort_values('elo', ascending=False)
)

output_df.head()

spread.df_to_sheet(df=output_df, sheet='stats')

spread.df_to_sheet(df=per_game_elo_df, sheet='elo_over_time')

# This is all network graph stuff
players_stats_df = spread.sheet_to_df(index=0, sheet='player_stats')

team_wins = (
    players_stats_df[['game_id', 'team_id', 'win', 'ign']]
    .merge(
        players_stats_df[['game_id', 'team_id', 'ign']],
        left_on=['game_id', 'team_id'],
        right_on=['game_id', 'team_id']
    )
    .astype({"win": int})
    .groupby(['ign_x', 'ign_y'])
    .agg({"game_id": "nunique", "win": "sum"})
    .reset_index()
    .rename(columns={"game_id": "teammates_games_played", "win": "teammates_games_won"})
)


h2h_wins = (
    players_stats_df[['game_id', 'team_id', 'win', 'ign']]
    .merge(
        players_stats_df[['game_id', 'team_id', 'ign']],
        left_on=['game_id'],
        right_on=['game_id']
    )
    .loc[lambda d: d['team_id_x'] != d['team_id_y'], :]
    .astype({"win": int})
    .groupby(['ign_x', 'ign_y'])
    .agg({"game_id": "nunique", "win": "sum"})
    .reset_index()
    .rename(columns={"game_id": "h2h_games_played", "win": "h2h_games_won"})
)

network_graph_df = (
    team_wins
    .merge(h2h_wins, how='outer')
    .assign(direction=lambda d: d['ign_x'] + '->' + d['ign_y'])
    .rename(columns={"ign_x": "player_1", "ign_y": "player_2"})
    .groupby(['player_1', 'player_2', 'direction'])
    .agg({"teammates_games_played": "max", "teammates_games_won": "max", "h2h_games_played": "max", "h2h_games_won": "max"})
    .reset_index()
    .assign(X=lambda d: np.random.randint(-300, 300, d.shape[0]),
            Y=lambda d: np.random.randint(-300, 300, d.shape[0])
            )
)

dummy_df = (
    network_graph_df
    .assign(X=0,
            Y=0)
)


network_graph_df = network_graph_df.append(dummy_df)

spread.df_to_sheet(df=network_graph_df, sheet='network_graph')
