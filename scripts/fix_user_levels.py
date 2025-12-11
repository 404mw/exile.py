"""
Fix user levels based on XP against levelCosts.json

This script reads user_levels.json and levelCosts.json, then recalculates
each user's level based on their total XP using the correct cumulative
XP requirements from levelCosts.json.

levelCosts.json contains cumulative XP required to reach each level:
- Level 1: 103 XP
- Level 2: 327 XP (cumulative, not 103+224)
- etc.
"""
import json
import os
from pathlib import Path


def get_level_for_xp(xp: int, level_costs: dict) -> int:
    """Calculate what level a user should be at for given XP.
    
    Args:
        xp: Total XP the user has
        level_costs: Dict mapping level (int) to cumulative XP required
        
    Returns:
        The highest level the user can reach with their XP
    """
    level = 0
    
    for lv in sorted(level_costs.keys()):
        if xp >= level_costs[lv]:
            level = lv
        else:
            break
    
    return level


def fix_user_levels():
    """Read user_levels.json and fix levels based on XP and levelCosts.json"""
    
    # Get the directory where the script is located
    script_dir = Path(__file__).resolve().parent.parent
    data_dir = script_dir / 'data'
    
    user_levels_path = data_dir / 'user_levels.json'
    level_costs_path = data_dir / 'levelCosts.json'
    
    # Check if files exist
    if not user_levels_path.exists():
        print(f"Error: {user_levels_path} not found.")
        return
    
    if not level_costs_path.exists():
        print(f"Error: {level_costs_path} not found.")
        return
    
    # Load the JSON files
    print(f"Loading user levels from: {user_levels_path}")
    try:
        with open(user_levels_path, 'r', encoding='utf-8') as f:
            user_levels = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading {user_levels_path}: {e}")
        return
    
    print(f"Loading level costs from: {level_costs_path}")
    try:
        with open(level_costs_path, 'r', encoding='utf-8') as f:
            level_costs_str = json.load(f)
            # Convert string keys to integers
            level_costs = {int(k): v for k, v in level_costs_str.items()}
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error reading {level_costs_path}: {e}")
        return
    
    # Fix levels
    print("\nRecalculating levels...")
    changes = 0
    
    for user_id, user_data in user_levels.items():
        old_level = user_data.get("level", 0)
        xp = user_data.get("xp", 0)
        
        # Calculate correct level
        new_level = get_level_for_xp(xp, level_costs)
        
        if old_level != new_level:
            changes += 1
            print(f"  {user_data.get('username', user_id)}: Level {old_level} → {new_level} (XP: {xp})")
            user_data["level"] = new_level
    
    # Save the updated data
    print(f"\nSaving {changes} corrected levels to: {user_levels_path}")
    try:
        with open(user_levels_path, 'w', encoding='utf-8') as f:
            json.dump(user_levels, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully fixed {changes} user level(s).")
    except IOError as e:
        print(f"Error writing {user_levels_path}: {e}")


if __name__ == "__main__":
    fix_user_levels()
