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
    Calculate total XP earned based on user's roles, channel context, and level.
    
    Four-tier calculation:
    1. Static additions (+ amount)
    2. Normal multipliers (* amount)  
    3. Level multiplier (* amount based on user level)
    4. True multiplier (* amount) - applied last
    
    Args:
        base_xp: Base XP amount
        member: Discord Member object
        channel_id: Channel where message was sent
        user_id: Discord user ID to look up current level
        
    Returns:
        Tuple of (total_xp, breakdown_dict)
        breakdown_dict contains:
        - base_xp: Initial base XP
        - static_additions: List of static bonuses
        - static_total: Sum of static additions
        - multiplier_values: List of normal multipliers
        - multiplier_product: Product of normal multipliers
        - level_multiplier: Level-based multiplier value
        - true_multiplier: Final true multiplier value
        - total_xp: Final calculated XP
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
    Get detailed breakdown of XP calculation for display purposes.
    
    Returns dict containing:
    - base_xp: Initial XP
    - static_additions: List of static bonuses applied
    - static_total: Sum of static additions
    - subtotal_after_static: base_xp + static_total
    - multiplier_values: List of normal multipliers
    - multiplier_product: Product of multipliers
    - subtotal_after_multipliers: subtotal_after_static * multiplier_product
    - level_multiplier: Level-based multiplier value
    - true_multiplier: Final multiplier value
    - total_xp: Final XP amount
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
    """Calculate what level a user should be at for a given total XP.
    
    levelCosts.json contains the XP required to reach each level (cumulative).
    For example: "1": 103 means you need 103 XP to reach level 1.
    
    Args:
        xp: Total XP the user has
        level_costs: Dict mapping level (as string) to cumulative XP required
        
    Returns:
        The highest level the user can reach with their XP
    """
    level = 0
    
    for lv in sorted([int(k) for k in level_costs.keys()]):
        if xp >= level_costs[str(lv)]:
            level = lv
        else:
            break
    
    return level

def get_xp_for_level(level: int, level_costs: Dict[str, int]) -> int:
    """Calculate total XP needed to reach a specific level.
    
    levelCosts.json contains cumulative XP required for each level.
    We just need to look up the level directly.
    
    Args:
        level: The level to get XP for
        level_costs: Dict mapping level (as string) to cumulative XP required
        
    Returns:
        Cumulative XP needed to reach that level
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
    Add XP to a user and check if they leveled up.
    
    Args:
        user_id: Discord user ID
        username: Discord username
        xp_amount: Amount of XP to add (should be pre-calculated via calculate_xp_from_context)
    
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
