import os
import json
from typing import List, Tuple, Dict

from .leveling import load_user_levels

def get_top_users(limit: int = 5) -> List[Tuple[str, Dict]]:
    """Return top users sorted by XP descending.

    Returns a list of tuples (user_id_str, user_data) limited by `limit`.
    """
    try:
        users = load_user_levels()
    except Exception:
        return []

    # users is a dict keyed by user id string
    sorted_users = sorted(users.items(), key=lambda kv: kv[1].get('xp', 0), reverse=True)
    return sorted_users[:limit]
