from Slitherai.Environment.Constants import MAX_LENGTH

CLOSEST_FOODS = 25
CLOSEST_PLAYERS = 10
OBSERVATION_SIZE = (
    (MAX_LENGTH - 1) * 2
    + 6
    + CLOSEST_FOODS * 3
    + CLOSEST_PLAYERS * (4 + 2 * MAX_LENGTH)
)
ACTION_LIST = [
    # W, A, S, D, Space
    (True, False, False, False, False),  # W
    (False, True, False, False, False),  # A
    (False, False, True, False, False),  # S
    (False, False, False, True, False),  # D
    (True, True, False, False, False),  # W + A
    (True, False, False, True, False),  # W + D
    (False, True, True, False, False),  # A + S
    (False, False, True, True, False),  # S + D
    (True, False, False, False, True),  # W + Space
    (False, True, False, False, True),  # A + Space
    (False, False, True, False, True),  # S + Space
    (False, False, False, True, True),  # D + Space
    (True, True, False, False, True),  # W + A + Space
    (True, False, False, True, True),  # W + D + Space
    (False, True, True, False, True),  # A + S + Space
    (False, False, True, True, True),  # S + D + Space
]
