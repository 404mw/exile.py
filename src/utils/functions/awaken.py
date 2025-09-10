import random, json, os, sys
sys.path.append(os.path.abspath("src"))

# reading json file 
with open("data/awaPool.json", "r") as f:
    curr_pool = json.load(f)

if not curr_pool["normal"]:
    from utils.awa_pool_buffed import pool
    pool_name: str = "buffed"
else:
    from utils.awa_pool import pool
    pool_name: str = "normal"


def get_random_answer(pool: list) -> str | None:
    """
    Get a random awakening result based on the probability distribution.
    
    Args:
        pool (list): List of possible awakening outcomes with their probabilities
        
    Returns:
        str | None: The selected awakening grade or None if an error occurs
    """
    random_value = random.random()
    cumulative_probability = 0.0

    for item in pool:
        cumulative_probability += item["probability"]
        if random_value < cumulative_probability:
            return item["answer"]

    return None  # Fallback in case of an error


def run_multiple_selections(iterations: int) -> dict:
    """
    Perform multiple awakening attempts and track results.
    
    Args:
        iterations (int): Number of awakening attempts to perform
        
    Returns:
        dict: Dictionary with awakening grades as keys and their counts as values
    """
    results = {item["answer"]: 0 for item in pool}
    
    for _ in range(iterations):
        result = get_random_answer(pool)
        if result is not None:
            results[result] += 1

    return results

def make_response(iterations: int, result_list: dict) -> str:
    """
    Format awakening results into a Discord message.
    
    Args:
        iterations (int): Number of awakening attempts performed
        result_list (dict): Dictionary of awakening results
        
    Returns:
        str: Formatted Discord message with awakening statistics
              including retire value, CSG cost, and gala points
    """
    retire = 0
    gala_points = 0
    csg: int = iterations * 100
    final_response: str = f"You awakened `{iterations}` times with **{pool_name}** odds\n\n"

    for index, value in enumerate(result_list.values()):
        if value:
            current_data = pool[index]
            final_response += f"- {current_data["emoji"]} x {value} -> {current_data['retire'] * value}\n"
            retire += current_data["retire"] * value
            gala_points += current_data["points"] * value

    final_response += f"\nCSG's Spent: `{csg}` \nRetired Amount: `{retire}` \nReturn Valued at: `{(retire/csg) * 100:.1f}%` \n\nPoints Earned for Gala: `{gala_points}`"

    return final_response



# result123 = run_multiple_selections(50)
# print(make_response(50, result123))