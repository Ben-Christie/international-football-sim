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

WC26_THIRD_PLACE_SLOTS = {
    'E': ['A', 'B', 'C', 'D', 'F'],
    'I': ['C', 'D', 'F', 'G', 'H'],
    'D': ['B', 'E', 'F', 'I', 'J'],
    'G': ['A', 'E', 'H', 'I', 'J'],
    'A': ['C', 'E', 'F', 'H', 'I'],
    'L': ['E', 'H', 'I', 'J', 'K'],
    'B': ['E', 'F', 'G', 'I', 'J'],
    'K': ['D', 'E', 'I', 'J', 'L'],
}

# some constants for the simulations
N_SIMULATIONS = 1
RANDOM_SEED = 42
# How much a result moves the elo rating
K_FACTOR_KO = 40
K_FACTOR_GROUP = 30
ELO_SCALE = 600  # division in the Elo formula
