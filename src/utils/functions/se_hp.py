from src.utils.se_hp_values import se_hp


def get_se_hp(hp: int, percentage: int = 100) -> str | None:
    """
Compute the HP value of a Star Expedition (SE) boss in Idle Heroes (IH).

Args:
    hp (int, required): Boss stage number (1–200).
    percentage (int, optional): Boss’s remaining HP %. 
        If omitted, assumes full HP.

Returns:
    float or None: The calculated boss HP, or None if invalid input.
"""

    bosshp = se_hp.get(hp)
    if bosshp is None:
        return None
    
    result = (bosshp * percentage) / 100
    return result