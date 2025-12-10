"""Helper to fetch XP required for a given level."""
from typing import Optional

from .leveling import load_level_costs, get_xp_for_level


def get_xp_required_for_level(level: int) -> Optional[int]:
    """Return cumulative XP required to reach a given level.
    
    Returns None if level is invalid or data cannot be loaded.
    """
    try:
        level_costs = load_level_costs()
        if not level_costs:
            return None
        
        return get_xp_for_level(level, level_costs)
    except Exception:
        return None
