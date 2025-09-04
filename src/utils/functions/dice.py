import random

def roll_dice(sides: int = 6) -> int:
    """
    Roll a dice with the given number of sides.
    Default: 6 sides.
    """
    if sides < 2:
        raise ValueError("Dice must have at least 2 sides.")
    return random.randint(1, sides)
