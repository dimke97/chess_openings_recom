import berserk
from datetime import datetime, date
import pandas as pd

# this is my security token, you have to create one
# if you want to check this script
# this is the URL adress: https://lichess.org/account/oauth/token
TOKEN = 'lip_DwfXziWN4IFt6PPyJkE6'
# This is my nickname
MY_ACCOUNT = 'dimke1997'

# Creating two object to access to my account and my games
my_session = berserk.TokenSession(TOKEN)
client = berserk.Client(session=my_session)

# %% Creating my rating history time serie
rating_history = client.users.get_rating_history('dimke1997')[1]['points']
rating_history = [list(r) for r in rating_history]

date_rating = []  # I'm putting datetimes here
rating = []  #
for rh in rating_history:
    year = rh[0]
    month = rh[1] + 1  # for some reason, months starting with 0
    day = rh[2]
    rtg = rh[3]
    dt = date(year, month, day)
    date_rating.append(dt)
    rating.append(rtg)

rating_series = pd.Series(data=rating,
                          index=date_rating,
                          dtype='int',
                          name='Rating History')
# This look good, but if i don't played at some day, index dosen't exist
# Let's fix this
rating_series.index = pd.to_datetime(rating_series.index)
start_end_serie = pd.date_range(
    rating_series.index.min(), rating_series.index.max())
start_end_serie = pd.Series(start_end_serie, name='new_index')
rating_merge = pd.merge(start_end_serie.reset_index(),
                        rating_series.reset_index(),
                        left_on='new_index',
                        right_on='index',
                        how='left')
rating_series = rating_merge[['new_index', 'Rating History']].copy()
rating_series['Rating History'] = rating_series['Rating History'].fillna(
    method='ffill')
rating_series = rating_series.set_index('new_index')
rating_series.plot()

rating_series.to_csv('rating_history.csv')

# %% Creating main dataframes of all my games from Lichess

# start_date = berserk.utils.to_millis(datetime(2021, 1, 1))
# end_date = berserk.utils.to_millis(datetime(2023, 2, 25))
my_games_object = client.games.export_by_player('dimke1997',
                                                perf_type='blitz',
                                                opening=True,
                                                tags=True,
                                                rated=True,
                                                moves=True)
# Creating list of all games - JSON format
my_games = list(my_games_object)

# Creating dictionary of all columns wich i want to use
main_dict = {'game_id': [],
             'white_player': [],
             'black_player': [],
             'white_elo': [],
             'black_elo': [],
             'game_started_at': [],
             'game_ended_at': [],
             'moves': [],
             'winner': [],
             'status': [],
             'eco': [],
             'name_of_opening': [],
             }

for my_gms in my_games:
    main_dict['game_id'].append(my_gms['id'])
    main_dict['white_player']\
        .append(my_gms['players']['white']['user']['name'])
    main_dict['black_player']\
        .append(my_gms['players']['black']['user']['name'])
    main_dict['white_elo'].append(my_gms['players']['white']['rating'])
    main_dict['black_elo'].append(my_gms['players']['black']['rating'])
    main_dict['game_started_at'].append(my_gms['createdAt'])
    main_dict['game_ended_at'].append(my_gms['lastMoveAt'])
    main_dict['moves'].append(my_gms['moves'])
    if 'winner' in my_gms:
        main_dict['winner'].append(my_gms['winner'])
    else:
        main_dict['winner'].append('draw')
    main_dict['status'].append(my_gms['status'])

    if 'opening' in my_gms:
        main_dict['eco'].append(my_gms['opening']['eco'])
        main_dict['name_of_opening'].append(my_gms['opening']['name'])
    else:
        main_dict['eco'].append('unknown')
        main_dict['name_of_opening'].append('unknown')

# Crating main DataFrame and start analyzing this :)
main_df = pd.DataFrame(main_dict)

# Adding some columns
main_df['game_duration'] = main_df['game_ended_at'] - \
    main_df['game_started_at']
main_df['num_of_moves'] = main_df['moves'].apply(
    lambda x: len(list(x.split(' ')))//2)

main_df.to_csv('my_games.csv', index=False)
