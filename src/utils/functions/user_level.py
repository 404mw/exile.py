import os
import json
from typing import Optional, Dict

from .leveling import load_user_levels, get_user_level_info

LEVEL_DATA_PATH = os.path.join(os.path.dirname(__file__), "../../..", "data", "user_levels.json")


def fetch_user_level(user_id: int) -> Optional[Dict]:
    """Return user level info for a given user id.

    Uses `get_user_level_info` from `leveling.py` to provide xp, level and progress.
    Returns None if user not found.
    """
    try:
        return get_user_level_info(user_id)
    except Exception:
        # Fallback to direct loading
        try:
            data = load_user_levels()
            return data.get(str(user_id))
        except Exception:
            return None
