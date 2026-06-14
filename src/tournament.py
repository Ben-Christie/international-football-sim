from match_simulator import simulate_match
from config import WC26GROUPS, WC26_THIRD_PLACE_SLOTS
from data_loader import load_data

# init a group
def initialise_group(group):
    group_table = []

    for team in group:
        group_table.append(
            {
                'team': team,
                'played': 0,
                'win': 0,
                'draw': 0,
                'loss': 0,
                'gf': 0,
                'ga': 0,
                'gd': 0,
                'pts': 0
            }
        )

    return group_table

def update_group(team_a, team_b, df):
    match_result, team_a_goals, team_b_goals = simulate_match(team_a['team'], team_b['team'], 'G', df)
    
    team_a['played'] += 1
    team_b['played'] += 1
    
    # update match results
    if match_result == 'A':
        team_a['win'] += 1
        team_a['pts'] += 3
        team_b['loss'] += 1
    elif match_result == 'B':
        team_b['win'] += 1
        team_b['pts'] += 3
        team_a['loss'] += 1
    elif match_result == 'D':
        team_a['draw'] += 1
        team_a['pts'] += 1
        team_b['draw'] += 1
        team_b['pts'] += 1
    
    # update goal difference
    team_a['gf'] += team_a_goals
    team_a['ga'] += team_b_goals
    team_a['gd'] += team_a_goals - team_b_goals
    team_b['gf'] += team_b_goals
    team_b['ga'] += team_a_goals
    team_b['gd'] += team_b_goals - team_a_goals
    
    return f"{team_a['team']} {team_a_goals} - {team_b_goals} {team_b['team']}"


def simulate_group(group_table, df):
    seed1 = group_table[0]
    seed2 = group_table[1]
    seed3 = group_table[2]
    seed4 = group_table[3]

    results = []
    results.append(update_group(seed1, seed2, df))
    results.append(update_group(seed3, seed4, df))
    results.append(update_group(seed1, seed3, df))
    results.append(update_group(seed4, seed2, df))
    results.append(update_group(seed4, seed1, df))
    results.append(update_group(seed2, seed3, df))

    return results

def sort_table(group_table, df):
    return sorted(
        group_table,
        key=lambda x: (
            x['pts'],
            x['gd'],
            x['gf'],
            x['win'],
            df.loc[x['team'], 'Rating']
        ),
        reverse=True
    )

def print_group_table(group_name, group_table, df):
    # sort table
    sorted_table = sort_table(group_table, df)
    
    print(f"\n{'='*70}")
    print(f"  GROUP {group_name}")
    print(f"{'='*70}")
    print(f"{'Pos':<4} {'Team':<25} {'P':<4} {'W':<4} {'D':<4} {'L':<4} {'GF':<4} {'GA':<4} {'GD':<5} {'PTS'}")
    print(f"{'─'*70}")
    
    for i, team in enumerate(sorted_table, 1):
        print(f"{i:<4} {team['team']:<25} {team['played']:<4} {team['win']:<4} {team['draw']:<4} {team['loss']:<4} {team['gf']:<4} {team['ga']:<4} {team['gd']:<5} {team['pts']}")
    print(f"{'='*70}")
    
def get_qualifiers(group_standings, df):
    winners = {}
    runners_up = {}
    third_places = []
    
    for group_name, group_table in group_standings.items():
        sorted_table = sort_table(group_table, df)
        winners[group_name] = sorted_table[0]
        runners_up[group_name] = sorted_table[1]
        # add group name to the dictionary so we know what group they below to ** unpacks the dict to allow this
        third_places.append({**sorted_table[2], 'group': group_name})
    
    third_places = sort_table(third_places, df)[:8]
    
    return winners, runners_up, third_places


def assign_third_place(best_third_places, third_place_slots):
    # map each qualifying group letter to its 3rd place team
    third_by_group = {team['group']: team for team in best_third_places}
    qualifying_groups = set(third_by_group.keys())

    # assignment maps winner group letter -> 3rd place team they will face
    assignment = {}

    def backtrack(slots_remaining, used_groups):
        # base case - all slots filled
        if not slots_remaining:
            return True

        current_slot = slots_remaining[0]
        rest_of_slots = slots_remaining[1:]

        # find which qualifying groups are eligible for this slot and not yet used
        eligible_groups = [
            group for group in third_place_slots[current_slot]
            if group in qualifying_groups
            and group not in used_groups
        ]

        # try each eligible group and backtrack if it leads to a dead end
        for group in eligible_groups:
            assignment[current_slot] = third_by_group[group]
            if backtrack(rest_of_slots, used_groups | {group}):
                return True
            del assignment[current_slot]

        return False

    backtrack(list(third_place_slots.keys()), set())
    return assignment

def simulate_knockouts(winners, runners_up, third_place, df):
    knockout_bracket = [
        winners['E'], 
        third_place['E'],
        winners['I'],
        third_place['I'],
        runners_up['A'],
        runners_up['B'],
        winners['F'],
        runners_up['C'],
        runners_up['K'],
        runners_up['L'],
        winners['H'],
        runners_up['J'],
        winners['D'],
        third_place['D'],
        winners['G'],
        third_place['G'],
        winners['C'],
        runners_up['F'],
        runners_up['E'],
        runners_up['I'],
        winners['A'],
        third_place['A'],
        winners['L'],
        third_place['L'],
        winners['J'],
        runners_up['H'],
        runners_up['D'],
        runners_up['G'],
        winners['B'],
        third_place['B'],
        winners['K'],
        third_place['K']
    ]
    
    # sim to final
    round_names = ['ROUND OF 32', 'ROUND OF 16', 'QUARTER FINALS', 'SEMI FINALS', 'FINAL']

    round_index = 0

    while len(knockout_bracket) > 1:
        print(f"\n{'='*70}")
        print(f"  {round_names[round_index]}")
        print(f"{'='*70}")

        next_round = []

        for i in range(0, len(knockout_bracket), 2):
            team_a = knockout_bracket[i]
            team_b = knockout_bracket[i + 1]

            match_result, goals_a, goals_b = simulate_match(
                team_a['team'], team_b['team'], 'KO', df)
            winner = team_a if match_result == 'A' else team_b

            print(f"  {team_a['team']} {goals_a} - {goals_b} {team_b['team']}")
            next_round.append(winner)

        knockout_bracket = next_round
        round_index += 1

    print(f"\n🏆 WORLD CUP 2026 CHAMPION: {knockout_bracket[0]['team']} 🏆")

def simulate_tournament(groups, df):
    group_standings = {
        'A': initialise_group(groups['A']),
        'B': initialise_group(groups['B']),
        'C': initialise_group(groups['C']),
        'D': initialise_group(groups['D']),
        'E': initialise_group(groups['E']),
        'F': initialise_group(groups['F']),
        'G': initialise_group(groups['G']),
        'H': initialise_group(groups['H']),
        'I': initialise_group(groups['I']),
        'J': initialise_group(groups['J']),
        'K': initialise_group(groups['K']),
        'L': initialise_group(groups['L'])
    }
    
    for letter, group_table in group_standings.items():
        results = simulate_group(group_table, df)
        print_group_table(letter, group_table, df)
        
        print(f"\n  RESULTS")
        print(f"  {'─'*40}")
        for result in results:
            print(f"  {result}")
    
    # get the winners, runners up and third place teams from the group stages
    winners, runners_up, best_third_places = get_qualifiers(group_standings, df)
    
    assignment = assign_third_place(best_third_places, WC26_THIRD_PLACE_SLOTS)
    
    simulate_knockouts(winners, runners_up, assignment, df)

# -------------------- RUN TOURNAMENT --------------------
# load data
df = load_data()

simulate_tournament(WC26GROUPS, df)