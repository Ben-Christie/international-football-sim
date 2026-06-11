from data_loader import load_data
from config import ELO_SCALE, K_FACTOR
import random

# load in data for elo ratings
df = load_data()

# update elo rating for both teams base don result
def update_elo(team_a, team_b, df):
    old_elo_a = df.loc[team_a]['Rating']
    old_elo_b = df.loc[team_b]['Rating']

    # get expected percentage win for A and B
    expected_win_a = get_win_probability(team_a, team_b, df)
    expected_win_b = 1 - expected_win_a

    match_result = simulate_match(team_a, team_b, df)

    # retrieve the meaning of the actual result numerically
    if match_result == 'A':
        actual_win_a, actual_win_b = 1, 0
    elif match_result == 'D':
        actual_win_a, actual_win_b = 0.5, 0.5
    elif match_result == 'B':
        actual_win_a, actual_win_b = 0, 1

    # calculate new elo rating based on results
    new_elo_a = old_elo_a + K_FACTOR * (actual_win_a - expected_win_a)
    new_elo_b = old_elo_b + K_FACTOR * (actual_win_b - expected_win_b)

    # update data in df to match new results and maintain momentum (or lack of)
    df.loc[team_a, 'Rating'] = round(new_elo_a)
    df.loc[team_b, 'Rating'] = round(new_elo_b)

# simulate a match between team A and team B based on the win percentages derived below
def simulate_match(team_a, team_b, df):
    p_win, p_draw, p_loss = get_match_probabilities(team_a, team_b, df)

    # A = team A win, D = draw, B = team B win
    return (random.choices(['A', 'D', 'B'], weights=[p_win, p_draw, p_loss], k=1))[0]


# get the likelihood of a win, draw and loss for team a against team b
def get_match_probabilities(team_a, team_b, df):
    # win prob
    p_win = get_win_probability(team_a, team_b, df)

    # base draw - standard value based on both teams draw percentage
    base_draw = (df.loc[team_a]['Draw Percentage'] +
                 df.loc[team_b]['Draw Percentage']) / 2

    # closeness measures how evenly matched two teams are (0 = mismatch, 1 = equal)
    # the closer the match, the higher the draw probability
    # e.g. p_win=0.5 -> closeness=1.0, p_win=0.9 -> closeness=0.2
    closeness = 1 - abs(p_win - 0.5) * 2
    p_draw = base_draw * closeness

    p_loss = 1 - p_win - p_draw

    return p_win, p_draw, p_loss


# win probability of A beating B - this is a helper function
def get_win_probability(team_a, team_b, df):
    elo_a = df.loc[team_a]['Rating']
    elo_b = df.loc[team_b]['Rating']

    team_a_win_prob = 1 / (1 + pow(10, (elo_b - elo_a) / ELO_SCALE))

    return team_a_win_prob
