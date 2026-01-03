"""
Leveling system functions for managing user XP and levels.
Implements a four-tier XP calculation system:
1. Static additions: flat XP bonuses (added first)
2. Normal multipliers: multiplicative bonuses (applied to base + static)
3. Level multiplier: bonus based on user's current level
4. True multiplier: final multiplier (applied last)
"""
import json
import os
from typing import Dict, Tuple, Optional, List
import nextcord
from ..types.user_level import UserLevel
from ..config import config, channels, roles

LEVEL_DATA_PATH = os.path.join(os.path.dirname(__file__), "../../..", "data", "user_levels.json")
LEVEL_COSTS_PATH = os.path.join(os.path.dirname(__file__), "../../..", "data", "levelCosts.json")


# ============================================================================
# XP CALCULATION SYSTEM
# ============================================================================

def calculate_xp_from_context(
    base_xp: int,
    member: nextcord.Member,
    channel_id: int,
    user_id: int
) -> Tuple[int, Dict[str, object]]:
    """
    Calculates the total XP a user should receive based on a variety of contextual factors.

    This function implements a four-tier XP calculation system:
    1.  **Static Additions:** Flat XP bonuses from channels or roles are added to the base XP.
    2.  **Normal Multipliers:** The result is then multiplied by any channel or role-based multipliers.
    3.  **Level Multiplier:** A multiplier based on the user's current level is applied.
    4.  **True Multiplier:** A final, overriding multiplier (e.g., for a special event role) is applied.

    Args:
        base_xp: The initial amount of XP before any modifications.
        member: The `nextcord.Member` object for the user who sent the message, used to check roles.
        channel_id: The ID of the channel where the message was sent, used to check for channel-specific bonuses.
        user_id: The ID of the user, used to fetch their current level for the level multiplier.

    Returns:
        A tuple containing:
        - The final, calculated total XP as an integer.
        - A dictionary detailing the breakdown of the calculation for logging or debugging purposes.
          Example:
          {
              "base_xp": 10,
              "static_additions": [{"source": "channel_123", "amount": 5}],
              "static_total": 5,
              "multiplier_values": [{"source": "role_456", "value": 1.5}],
              "multiplier_product": 1.5,
              "level_multiplier": 1.02,
              "true_multiplier": 1.0,
              "total_xp": 15
          }
    """
    
    breakdown = {
        "base_xp": base_xp,
        "static_additions": [],
        "static_total": 0,
        "multiplier_values": [],
        "multiplier_product": 1.0,
        "level_multiplier": 1.0,
        "true_multiplier": 1.0,
        "total_xp": base_xp,
    }
    
    # ========== STEP 1: Calculate static additions ==========
    static_total = 0
    
    # Check channel for static additions
    if hasattr(channels, 'xp_bonuses'):
        for bonus in channels.xp_bonuses:
            if bonus.id == channel_id:
                breakdown["static_additions"].append({
                    "source": f"channel_{bonus.id}",
                    "amount": bonus.amount
                })
                static_total += bonus.amount
    
    # Check roles for static additions
    if hasattr(roles, 'xp_bonuses') and hasattr(member, 'roles'):
        for role in member.roles:
            for bonus in roles.xp_bonuses:
                if bonus.id == role.id:
                    breakdown["static_additions"].append({
                        "source": f"role_{bonus.id}",
                        "amount": bonus.amount
                    })
                    static_total += bonus.amount
    
    breakdown["static_total"] = static_total
    
    # ========== STEP 2: Calculate normal multipliers ==========
    xp_after_static = base_xp + static_total
    multiplier_product = 1.0
    
    # Check channel for multipliers
    if hasattr(channels, 'xp_multipliers'):
        for multiplier in channels.xp_multipliers:
            if multiplier.id == channel_id:
                breakdown["multiplier_values"].append({
                    "source": f"channel_{multiplier.id}",
                    "value": multiplier.value
                })
                multiplier_product *= multiplier.value
    
    # Check roles for multipliers
    if hasattr(roles, 'xp_multipliers') and hasattr(member, 'roles'):
        for role in member.roles:
            for multiplier in roles.xp_multipliers:
                if multiplier.id == role.id:
                    breakdown["multiplier_values"].append({
                        "source": f"role_{multiplier.id}",
                        "value": multiplier.value
                    })
                    multiplier_product *= multiplier.value
    
    breakdown["multiplier_product"] = multiplier_product
    
    # ========== STEP 3: Calculate level-based multiplier ==========
    level_multiplier = 1.0
    user_level_info = get_user_level_info(user_id)
    
    if user_level_info and hasattr(config, 'level_multiplier_rate'):
        user_level = user_level_info.get("level", 1)
        level_multiplier = 1.0 + (user_level * config.level_multiplier_rate)
        breakdown["level_multiplier"] = level_multiplier
        breakdown["multiplier_values"].append({
            "source": f"level_{user_level}",
            "value": level_multiplier
        })
    
    # ========== STEP 4: Apply true multiplier ==========
    true_multiplier = 1.0
    
    if hasattr(roles, 'xp_true_multipliers') and hasattr(member, 'roles'):
        for role in member.roles:
            for true_mult in roles.xp_true_multipliers:
                if true_mult.id == role.id:
                    true_multiplier = true_mult.value
                    break
    
    breakdown["true_multiplier"] = true_multiplier
    
    # ========== FINAL CALCULATION ==========
    # (base_xp + static_additions) * multiplier_product * level_multiplier * true_multiplier
    total_xp = int(xp_after_static * multiplier_product * level_multiplier * true_multiplier)
    breakdown["total_xp"] = total_xp
    
    return total_xp, breakdown


def get_xp_breakdown(
    base_xp: int,
    member: nextcord.Member,
    channel_id: int,
    user_id: int
) -> Dict[str, object]:
    """
    Provides a detailed, user-friendly breakdown of an XP calculation.

    This function is a wrapper around `calculate_xp_from_context` that adds
    intermediate subtotals to the breakdown, making it easier to display the
    calculation step-by-step.

    Args:
        base_xp: The initial amount of XP before any modifications.
        member: The `nextcord.Member` object for the user.
        channel_id: The ID of the channel where the message was sent.
        user_id: The ID of the user.

    Returns:
        A dictionary containing a comprehensive breakdown of the XP calculation,
        including intermediate subtotals.
    """
    
    _, breakdown = calculate_xp_from_context(base_xp, member, channel_id, user_id)
    
    # Add intermediate calculations for clarity
    breakdown["subtotal_after_static"] = base_xp + breakdown["static_total"]
    breakdown["subtotal_after_multipliers"] = int(
        breakdown["subtotal_after_static"] * breakdown["multiplier_product"]
    )
    
    return breakdown


# ============================================================================
# LEVEL MANAGEMENT
# ============================================================================

def load_level_costs() -> Dict[str, int]:
    """
    Loads the level cost data from the corresponding JSON file.

    The levelCosts.json file is expected to be a dictionary mapping level
    numbers (as strings) to the cumulative XP required to reach that level.

    Returns:
        A dictionary of level costs. Returns an empty dictionary if the file
        is not found or contains invalid JSON.
    """
    try:
        with open(LEVEL_COSTS_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Error loading level costs from {LEVEL_COSTS_PATH}")
        return {}

def load_user_levels() -> Dict[str, Dict]:
    """
    Loads all user level and XP data from the user_levels.json file.

    Returns:
        A dictionary where keys are user IDs (as strings) and values are
        dictionaries containing user data (e.g., username, xp, level).
        Returns an empty dictionary if the file is not found or is empty.
    """
    try:
        with open(LEVEL_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user_levels(data: Dict[str, Dict]) -> None:
    """
    Saves the provided user level data to the user_levels.json file.

    This function will create the data directory if it doesn't exist.
    The data is saved in a human-readable format with an indent of 2.

    Args:
        data: A dictionary containing all user level data to be saved.
    """
    os.makedirs(os.path.dirname(LEVEL_DATA_PATH), exist_ok=True)
    with open(LEVEL_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_level_for_xp(xp: int, level_costs: Dict[str, int]) -> int:
    """
    Determines a user's level based on their total accumulated XP.

    It iterates through the sorted level costs and finds the highest level
    the user has achieved.

    Args:
        xp: The total XP of the user.
        level_costs: A dictionary mapping level numbers to cumulative XP costs.

    Returns:
        The calculated level for the given XP. Returns 0 if the user's XP
        doesn't meet the requirement for level 1.
    """
    level = 0
    
    for lv in sorted([int(k) for k in level_costs.keys()]):
        if xp >= level_costs[str(lv)]:
            level = lv
        else:
            break
    
    return level

def get_xp_for_level(level: int, level_costs: Dict[str, int]) -> int:
    """
    Retrieves the total cumulative XP required to reach a specific level.

    Args:
        level: The level to look up.
        level_costs: A dictionary mapping level numbers to cumulative XP costs.

    Returns:
        The cumulative XP required for the given level. Returns 0 if the
        level is not found in the `level_costs` dictionary.
    """
    if str(level) in level_costs:
        return level_costs[str(level)]
    return 0

def add_xp(
    user_id: int,
    username: str,
    xp_amount: int
) -> Tuple[bool, int, int]:
    """
    Adds a specified amount of XP to a user and updates their level.

    This function handles loading user data, adding XP, checking for level ups,
    and saving the updated data. If the user does not exist in the data file,
    they will be created.

    Args:
        user_id: The Discord ID of the user.
        username: The current username of the user (will be updated in the data).
        xp_amount: The amount of XP to add (should be pre-calculated).

    Returns:
        A tuple containing:
        - A boolean indicating if the user leveled up (`True` if they did, `False` otherwise).
        - The user's new level.
        - The user's old level.
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
    """
    Retrieves detailed level and XP information for a specific user.

    This is useful for displaying user stats, such as in a profile or
    leaderboard command.

    Args:
        user_id: The Discord ID of the user to look up.

    Returns:
        A dictionary containing detailed user stats if the user is found,
        otherwise `None`. The dictionary includes:
        - `username`: The user's name.
        - `xp`: The user's total XP.
        - `level`: The user's current level.
        - `xp_for_next_level`: The amount of XP needed to get from the start
          of the current level to the next level.
        - `xp_progress`: The user's XP progress within the current level.
    """
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
