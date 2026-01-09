from pydantic import BaseModel
from src.utils.dt_cost import dt_cost
from src.utils.temple_cost import temple_cost

# Type definition for the return dictionary
class ReturnDict(BaseModel):
        user_gems: int | None = 0
        user_spirits: int | None = 0
        required_gems: int | None = 0
        required_spiritveins: int | None = 0
        error: str | None = None

def get_dt_calc(
        *,
        goal_temple: int,
        origin: int = 0,
        surge: int = 0,
        chaos: int = 0,
        core: int = 0,
        polystar: int = 0,
        nirvana: int = 0,
        bag_gems: int = 0,
        bag_spirit: int = 0
    ) -> ReturnDict:
    """
    Calculates the required resources (gems and spiritveins) needed to reach a specific temple level, can also be used to get the required temple resources only.
    
    Args:
        goal_temple (int, required): Target temple level (1-22)
        origin (int, optional): Number of Origin/D1 ranks. (0-16).
        surge (int, optional): Number of Surge/D2 ranks. (0-16).
        chaos (int, optional): Number of Chaos/D3 ranks. (0-16).
        core (int, optional): Number of Core/D4 ranks. (0-16).
        polystar (int, optional): Number of Polystar/D5 ranks. (0-16).
        nirvana (int, optional): Number of Nirvana/D6 ranks. (0-12).
        bag_gems (int, optional): Current number of Aurora Gems in bag. (1-100).
        bag_spirit (int, optional): Current number of Scattered Spiritvein Shards in bag. (1-999999).
    
    Returns:
        A dictionary containing users and required [gems and spiritveins], or an error message if input is invalid.
    """
    # Validate input
    if goal_temple < 1:
        return ReturnDict(error = "goal_temple must be greater than 0")

    # Initialize resource counters with current bag contents
    total_gems: int = bag_gems
    total_spirits: int = bag_spirit
    
    # Get temple requirements or return error if invalid
    try:
        temple = temple_cost[goal_temple - 1]
    except IndexError:
        return ReturnDict(error = f"Invalid goal_temple value: {goal_temple}")
        
    # List of ranks in order of progression
    dt_ranks: list[int] = [origin, surge, chaos, core, polystar, nirvana]

    # Calculate total resources from each rank
    for rank_index, rank_count in enumerate(dt_ranks):
        if rank_count > 0:
            # Add resources based on rank cost multiplied by number of ranks
            total_gems += dt_cost[rank_index].gems * rank_count
            total_spirits += dt_cost[rank_index].spiritvein * rank_count

    # Calculate remaining required resources
    result: ReturnDict = ReturnDict(
         user_gems = total_gems,
         user_spirits = total_spirits,
         required_gems = temple.gem - total_gems,
         required_spiritveins = temple.spiritvein - total_spirits
    )
    return result
