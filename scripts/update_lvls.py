import json
import os
from pathlib import Path

def update_user_levels():
    """
    Reads 'raw.json' and 'level_cost.json', updates user XP,
    calculates the new level based on 'level_cost.json', and
    saves the updated data to 'updated_data.json'.
    """
    # 1. Define File Paths
    # Assumes the script is run from the directory *containing* the 'data' folder
    # or it is smart enough to navigate to the correct parent directory if placed inside 'data'.
    
    # Get the directory where the script is located
    script_dir = Path(__file__).resolve().parent.parent
    
    # Navigate to the 'data' directory (one level up, then into 'data')
    # If the script is executed from the same directory as 'data', use: data_dir = script_dir / 'data'
    # If the script is inside the 'data' folder, use: data_dir = script_dir
    # Based on the prompt's path: `go < (back to) one directory > data > raw.json`, 
    # we assume the script is executed/located *outside* the `data` folder.
    data_dir = script_dir / 'data'
    
    raw_json_path = data_dir / 'user_levels.json'
    level_cost_json_path = data_dir / 'levelCosts.json'
    output_json_path = data_dir / 'updated_data.json'

    # Check if data directory exists
    if not data_dir.is_dir():
        print(f"Error: Data directory not found at {data_dir}. Please create it and add the JSON files.")
        return

    # 2. Read JSON Files
    print(f"Reading raw data from: {raw_json_path}")
    try:
        with open(raw_json_path, 'r') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {raw_json_path} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {raw_json_path}.")
        return

    print(f"Reading level cost data from: {level_cost_json_path}")
    try:
        with open(level_cost_json_path, 'r') as f:
            level_cost_data_str = json.load(f)
            # Convert string keys (from JSON) to integers for proper comparison
            level_cost_data = {int(k): v for k, v in level_cost_data_str.items()}
    except FileNotFoundError:
        print(f"Error: {level_cost_json_path} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {level_cost_json_path}.")
        return

    # Sort the level cost keys (levels) in ascending order to easily find the highest level
    sorted_levels = sorted(level_cost_data.keys())
    
    # 3. Process and Update Data
    print("Processing user data...")
    updated_data = {}
    
    # Iterate through the nested dictionary of users
    for user_id, user_data in raw_data.items():
        # Get current XP and level
        current_xp = user_data.get('xp', 0)
        
        # Calculate the new XP
        # New XP = (Current XP / 10) * 35
        # Use integer division (//) for the first step if you prefer only integer results, 
        # but float is generally safer for calculations. We'll use float then round to int.
        new_xp = int((current_xp / 10) * 35)
        
        # Determine the new level
        new_level = 0
        
        # Iterate through the sorted levels to find the highest level the new XP can afford
        for level in sorted_levels:
            # Check if the accumulated XP cost for this level is less than or equal to the new XP
            if level_cost_data[level] <= new_xp:
                new_level = level
            else:
                # Since levels are sorted, we can stop checking once the cost is too high
                break
        
        # 4. Construct the Updated User Object
        # Copy the original data
        updated_user_data = user_data.copy()
        # Update the XP and Level
        updated_user_data['xp'] = new_xp
        updated_user_data['level'] = new_level
        
        # Add to the final output dictionary
        updated_data[user_id] = updated_user_data

    # 5. Write the Updated Data to a New JSON File
    print(f"Writing updated data to: {output_json_path}")
    try:
        with open(output_json_path, 'w') as f:
            json.dump(updated_data, f, indent=4)
        print("✅ Script completed successfully. Data saved as updated_data.json.")
    except Exception as e:
        print(f"Error writing file: {e}")


# Execute the function
if __name__ == "__main__":
    update_user_levels()