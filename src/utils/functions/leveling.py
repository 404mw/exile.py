"""
Leveling system functions for managing user XP and levels.
"""
import json
import os
from typing import Dict, Tuple, Optional
from ..types.user_level import UserLevel

LEVEL_DATA_PATH = os.path.join(os.path.dirname(__file__), "../../..", "data", "user_levels.json")
LEVEL_COSTS_PATH = os.path.join(os.path.dirname(__file__), "../../..", "data", "levelCosts.json")

def load_level_costs() -> Dict[str, int]:
    """Load level costs from levelCosts.json"""
    try:
        with open(LEVEL_COSTS_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error loading level costs from {LEVEL_COSTS_PATH}")
        return {}

def load_user_levels() -> Dict[str, Dict]:
    """Load all user levels from JSON file"""
    try:
        with open(LEVEL_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user_levels(data: Dict[str, Dict]) -> None:
    """Save user levels to JSON file"""
    os.makedirs(os.path.dirname(LEVEL_DATA_PATH), exist_ok=True)
    with open(LEVEL_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_level_for_xp(xp: int, level_costs: Dict[str, int]) -> int:
    """Calculate what level a user should be at for a given total XP"""
    level = 1
    total_xp_needed = 0
    
    for lv in sorted([int(k) for k in level_costs.keys()]):
        if xp >= total_xp_needed + level_costs[str(lv)]:
            total_xp_needed += level_costs[str(lv)]
            level = lv + 1
        else:
            break
    
    return level

def get_xp_for_level(level: int, level_costs: Dict[str, int]) -> int:
    """Calculate total XP needed to reach a specific level"""
    total_xp = 0
    for lv in range(1, level):
        if str(lv) in level_costs:
            total_xp += level_costs[str(lv)]
    return total_xp

def add_xp(user_id: int, username: str, xp_amount: int) -> Tuple[bool, int, int]:
    """
    Add XP to a user and check if they leveled up.
    
    Returns:
        Tuple of (leveled_up, new_level, old_level)
    """
    user_levels = load_user_levels()
    level_costs = load_level_costs()
    
    user_key = str(user_id)
    
    if user_key not in user_levels:
        user_levels[user_key] = {
            "username": username,
            "xp": 0,
            "level": 1,
        }
    
    user_data = user_levels[user_key]
    old_level = user_data["level"]
    
    # Add XP
    user_data["xp"] += xp_amount
    
    # Recalculate level based on total XP
    new_level = get_level_for_xp(user_data["xp"], level_costs)
    user_data["level"] = new_level
    user_data["username"] = username  # Update username in case it changed
    
    save_user_levels(user_levels)
    
    leveled_up = new_level > old_level
    return leveled_up, new_level, old_level

def get_user_level_info(user_id: int) -> Optional[Dict]:
    """Get level information for a specific user"""
    user_levels = load_user_levels()
    user_key = str(user_id)
    
    if user_key in user_levels:
        user_data = user_levels[user_key]
        level_costs = load_level_costs()
        
        xp_for_current_level = get_xp_for_level(user_data["level"], level_costs)
        xp_for_next_level = get_xp_for_level(user_data["level"] + 1, level_costs)
        xp_needed_for_next = xp_for_next_level - xp_for_current_level
        xp_progress = user_data["xp"] - xp_for_current_level
        
        return {
            **user_data,
            "xp_for_next_level": xp_needed_for_next,
            "xp_progress": xp_progress
        }
    
    return None
