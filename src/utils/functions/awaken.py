import random, json, os
from importlib import import_module
from typing import List, Dict, Any, Optional, Tuple

def get_current_pool() -> Tuple[List[Dict[str, Any]], str]:
    """
    Get the current pool configuration.
    
    Returns:
        tuple[list, str]: A tuple containing the pool data and pool name
    """
    # reading json file 
    with open("data/awaPool.json", "r") as f:
        curr_pool = json.load(f)

    if not curr_pool["normal"]:
        module = import_module("src.utils.awa_pool_buffed")
        pool = module.pool
        pool_name: str = "buffed"
    else:
        module = import_module("src.utils.awa_pool")
        pool = module.pool
        pool_name: str = "normal"
    
    return pool, pool_name


def get_random_answer(pool: Optional[List[Dict[str, Any]]] = None) -> Optional[str]:
    """
    Get a random awakening result based on the probability distribution.
    
    Args:
        pool (list): List of possible awakening outcomes with their probabilities
        
    Returns:
        str | None: The selected awakening grade or None if an error occurs
    """
    if pool is None:
        pool, _ = get_current_pool()
        
    random_value = random.random()
    cumulative_probability = 0.0

    for item in pool:
        cumulative_probability += item["probability"]
        if random_value < cumulative_probability:
            return item["answer"]

    return None


def run_multiple_selections(iterations: int) -> Tuple[Dict[str, int], List[Dict[str, Any]], str]:
    """
    Perform multiple awakening attempts and track results.
    
    Args:
        iterations (int): Number of awakening attempts to perform
        
    Returns:
        Tuple containing:
            - Dict[str, int]: Results count for each outcome
            - List[Dict[str, Any]]: Current pool configuration
            - str: Pool name (normal/buffed)
    """
    # Get current pool
    current_pool, pool_name = get_current_pool()
    
    # Initialize results tracking
    results = {item["answer"]: 0 for item in current_pool}
    
    # Perform awakenings
    for _ in range(iterations):
        result = get_random_answer(current_pool)
        if result is not None:
            results[result] += 1

    return results, current_pool, pool_name


def make_response(iterations: int) -> str:
    """
    Format awakening results into a Discord message.
    
    Args:
        iterations (int): Number of awakening attempts performed
        
    Returns:
        str: Formatted Discord message with awakening statistics
             including retire value, CSG cost, and gala points
    """
    results, pool, pool_name = run_multiple_selections(iterations)
    
    retire = 0
    gala_points = 0
    csg: int = iterations * 100
    final_response: str = f"You awakened `{iterations}` times with **{pool_name}** odds\n\n"

    for index, (result, count) in enumerate(results.items()):
        if count > 0:
            current_data = pool[index]
            final_response += f"- {current_data['emoji']} x {count} -> {current_data['retire'] * count}\n"
            retire += current_data["retire"] * count
            gala_points += current_data["points"] * count

    final_response += f"\nCSG's Spent: `{csg}` \nRetired Amount: `{retire}` \nReturn Valued at: `{(retire/csg) * 100:.1f}%` \n\nPoints Earned for Gala: `{gala_points}`"

    return final_response