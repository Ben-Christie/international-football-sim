from config import ELO_SCALE, K_FACTOR_GROUP, K_FACTOR_KO, K_FACTOR_FINAL
import random
import numpy as np

# simulate a match between team A and team B based on the win percentages derived below
def simulate_match(team_a, team_b, match_type, df):
    p_win, p_draw, p_loss = get_match_probabilities(team_a, team_b, df)

    # A = team A win, D = draw, B = team B win
    match_result = (random.choices(['A', 'D', 'B'], weights=[
                    p_win, p_draw, p_loss], k=1))[0]

    # no draws in knockout games - resimulate until we get a winner
    while match_type != 'G' and match_result == 'D':
        match_result = (random.choices(['A', 'D', 'B'], weights=[
                        p_win, p_draw, p_loss], k=1))[0]

    # create the score of the game
    team_a_goals, team_b_goals = get_score(team_a, team_b, match_result, df)

    # update data frame after each match
    update_df(team_a, team_b, match_result, team_a_goals, team_b_goals, df)

    # update elo rating after match
    update_elo(team_a, team_b, match_type, match_result, df)

    return match_result, team_a_goals, team_b_goals


def get_score(team_a, team_b, match_result, df):
    # rank each team on a bell curve for their goals scored and goals conceded
    xgf_percentile = df['Goals Scored 90'].rank(pct=True)
    # invert, less is good
    xga_percentile = 1 - df['Goals Conceded 90'].rank(pct=True)

    # get the specific teams rank
    team_a_xgf_percentile = xgf_percentile.loc[team_a]
    team_a_xga_percentile = xga_percentile.loc[team_a]

    team_b_xgf_percentile = xgf_percentile.loc[team_b]
    team_b_xga_percentile = xga_percentile.loc[team_b]

    # compete attack vs defense
    team_a_multiplier = team_a_xgf_percentile - team_b_xga_percentile
    team_b_multiplier = team_b_xgf_percentile - team_a_xga_percentile

    # get expected score for each team
    team_a_exp_score = max(
        0, df.loc[team_a, 'Goals Scored 90'] + (team_a_multiplier * 2))
    team_b_exp_score = max(
        0, df.loc[team_b, 'Goals Scored 90'] + (team_b_multiplier * 2))

    # correct scores to results
    if match_result == 'A' and team_a_exp_score < team_b_exp_score:
        team_b_exp_score = team_a_exp_score * 0.8
    elif match_result == 'B' and team_a_exp_score > team_b_exp_score:
        team_a_exp_score = team_b_exp_score * 0.8
    elif match_result == 'D':
        # draw - converge both to their average
        avg = max(0.75, (team_a_exp_score + team_b_exp_score) / 2)
        team_a_exp_score = avg
        team_b_exp_score = avg

    # create the final score
    while True:
        team_a_goals = np.random.poisson(team_a_exp_score)
        team_b_goals = np.random.poisson(team_b_exp_score)

        if match_result == 'A' and team_a_goals > team_b_goals:
            return team_a_goals, team_b_goals
        elif match_result == 'D' and team_a_goals == team_b_goals:
            return team_a_goals, team_b_goals
        elif match_result == 'B' and team_a_goals < team_b_goals:
            return team_a_goals, team_b_goals

# update elo rating for both teams base don result
def update_elo(team_a, team_b, match_type, match_result, df):
    # set K_FACTOR based on match type
    k_factor = K_FACTOR_GROUP
    if match_type == 'KO':
        k_factor = K_FACTOR_KO
    elif match_type == 'F':
        k_factor = K_FACTOR_FINAL

    old_elo_a = df.loc[team_a, 'Rating']
    old_elo_b = df.loc[team_b, 'Rating']

    # get expected percentage win for A and B
    expected_win_a = get_win_probability(team_a, team_b, df)
    expected_win_b = 1 - expected_win_a

    # retrieve the meaning of the actual result numerically
    if match_result == 'A':
        actual_win_a, actual_win_b = 1, 0
    elif match_result == 'D':
        actual_win_a, actual_win_b = 0.5, 0.5
    elif match_result == 'B':
        actual_win_a, actual_win_b = 0, 1

    # calculate new elo rating based on results
    new_elo_a = old_elo_a + k_factor * (actual_win_a - expected_win_a)
    new_elo_b = old_elo_b + k_factor * (actual_win_b - expected_win_b)

    # update data in df to match new results and maintain momentum (or lack of)
    df.loc[team_a, 'Rating'] = round(new_elo_a)
    df.loc[team_b, 'Rating'] = round(new_elo_b)

# get the likelihood of a win, draw and loss for team a against team b
def get_match_probabilities(team_a, team_b, df):
    # win prob
    p_win = get_win_probability(team_a, team_b, df)

    # base draw - standard value based on both teams draw percentage
    base_draw = ((df.loc[team_a, 'Draw Percentage'] +
                 df.loc[team_b, 'Draw Percentage']) / 2)

    # closeness measures how evenly matched two teams are (0 = mismatch, 1 = equal)
    # the closer the match, the higher the draw probability
    # e.g. p_win=0.5 -> closeness=1.0, p_win=0.9 -> closeness=0.2
    closeness = 1 - abs(p_win - 0.5) * 2
    p_draw = base_draw * closeness

    p_loss = 1 - p_win - p_draw

    return p_win, p_draw, p_loss


# win probability of A beating B - this is a helper function
def get_win_probability(team_a, team_b, df):
    elo_a = df.loc[team_a, 'Rating']
    elo_b = df.loc[team_b, 'Rating']

    form_a = df.loc[team_a, '1 Year Change Rating']
    form_b = df.loc[team_b, '1 Year Change Rating']

    # take into account some of the last year's form - teams trending up get a boost and vice versa
    adjusted_elo_a = elo_a + (form_a * 0.5)
    adjusted_elo_b = elo_b + (form_b * 0.5)

    team_a_exp_win_prob = 1 / \
        (1 + pow(10, (adjusted_elo_b - adjusted_elo_a) / ELO_SCALE))

    return team_a_exp_win_prob

def update_df(team_a, team_b, match_result, team_a_goals, team_b_goals, df):
    # update goals
    df.loc[team_a, 'Goals For'] += team_a_goals
    df.loc[team_a, 'Goals Against'] += team_b_goals
    df.loc[team_b, 'Goals For'] += team_b_goals
    df.loc[team_b, 'Goals Against'] += team_a_goals

    # update wins, losses, draws
    if match_result == 'A':
        df.loc[team_a, 'Wins'] += 1
        df.loc[team_b, 'Losses'] += 1
    elif match_result == 'D':
        df.loc[team_a, 'Draws'] += 1
        df.loc[team_b, 'Draws'] += 1
    elif match_result == 'B':
        df.loc[team_a, 'Losses'] += 1
        df.loc[team_b, 'Wins'] += 1

    # update total fixtures
    df.loc[team_a, 'Total Fixtures'] += 1
    df.loc[team_b, 'Total Fixtures'] += 1

    # recalculate per game stats
    for team in [team_a, team_b]:
        total = df.loc[team, 'Total Fixtures']
        df.loc[team, 'Goals Scored 90'] = df.loc[team, 'Goals For'] / total
        df.loc[team, 'Goals Conceded 90'] = df.loc[team, 'Goals Against'] / total
        df.loc[team, 'Win Percentage'] = df.loc[team, 'Wins'] / total
        df.loc[team, 'Draw Percentage'] = df.loc[team, 'Draws'] / total
        df.loc[team, 'Loss Percentage'] = df.loc[team, 'Losses'] / total
