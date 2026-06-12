import pandas as pd
from config import DATA_PATH


def load_data():
    # read the csv into a pandas dataframe
    df = pd.read_csv(DATA_PATH)

    # create percentages and add to df
    df['Win Percentage'] = df['Wins'] / df['Total Fixtures']
    df['Draw Percentage'] = df['Draws'] / df['Total Fixtures']
    df['Loss Percentage'] = df['Losses'] / df['Total Fixtures']

    # goal difference per game
    df['Goals Scored 90'] = df['Goals For'] / df['Total Fixtures']
    df['Goals Conceded 90'] = df['Goals Against'] / df['Total Fixtures']

    # set index to Nation so we can search for a row based on the name of the country
    # can use df.loc("Spain") for example to get Spain's data instead of needing an ID
    df = df.set_index('Nation')

    return df
