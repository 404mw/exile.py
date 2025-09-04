import sys, os
sys.path.append(os.path.abspath("src"))
from utils.se_hp_values import se_hp


def get_se_hp(hp: int, percentage: int = 100) -> str:
    """
Compute the HP value of a Star Expedition (SE) boss in Idle Heroes (IH).

Args:
    hp (int, required): Boss stage number (1–200).
    percentage (int, optional): Boss’s remaining HP %. 
        If omitted, assumes full HP.

Returns:
    str: The calculated boss HP.
"""

    bosshp = se_hp.get(hp)
    if bosshp is None:
        return f"{hp} isnt a valid input"
    
    result = (bosshp * percentage) / 100
    return str(result)