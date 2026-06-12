from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "elo-ratings.csv"

WC26GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czechia"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["USA", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# some constants for the simulations
N_SIMULATIONS = 1
RANDOM_SEED = 42
# How much a result moves the elo rating
K_FACTOR_FINAL = 60
K_FACTOR_KO = 50
K_FACTOR_GROUP = 40
ELO_SCALE = 600  # division in the Elo formula

# tournament configurations

WORLD_CUP = {
    "name": "FIFA World Cup 2026",
    "groups": WC26GROUPS,
    "group_stage": {
        "teams_per_group": 4,
        "qualify_per_group": 2,
        "best_third_places": 8,  # WC2026 specific
        "points": {"win": 3, "draw": 1, "loss": 0}
    },
    "knockout_rounds": ["R32", "R16", "QF", "SF", "F"],
    "match_types": {
        "group": "G",
        "knockout": "KO",
        "final": "F"
    }
}
