import json
from pydantic import BaseModel

class GrimCalcResult(BaseModel):
    """
    Data model for the result of a Grimoire cost calculation.
    """
    essence_cost: int = 0
    imprint_cost: int = 0
    essence_choices: float = 0.0
    imprint_choices: float = 0.0
    error: str | None = None

def _load_json_data(file_path: str) -> dict:
    """A utility function to load data from a specified JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {file_path} not found")
        return {}

def _calculate_event_choices(essence: int = 0, imprint: int = 0) -> tuple[float, float]:
    """Calculates the number of 'event choices' for essence and imprint."""
    essence_choices = essence / 1400000 if essence > 0 else 0
    imprint_choices = imprint / 175000 if imprint > 0 else 0
    return essence_choices, imprint_choices

def get_grim_calc(
    book: str,
    goal_lvl: int,
    current_lvl: int | None = None
) -> GrimCalcResult:
    """
    Calculates the resource cost to upgrade a Grimoire.

    Args:
        book: The type of Grimoire ('Enable' or 'Imprint').
        goal_lvl: The target level for the calculation.
        current_lvl: An optional current level to calculate the difference from.

    Returns:
        A GrimCalcResult object containing the calculated costs or an error.
    """
    grim1_cost = _load_json_data("data/grim1Cost.json")
    grim2_cost = _load_json_data("data/grim2Cost.json")

    if current_lvl is not None and goal_lvl <= current_lvl:
        return GrimCalcResult(error="Goal level must be higher than current level.")

    if book.lower() == "enable":
        cost_data = grim1_cost
    elif book.lower() == "imprint":
        cost_data = grim2_cost
    else:
        return GrimCalcResult(error="Invalid book type. Please choose 'Enable' or 'Imprint'.")

    goal_cost = cost_data.get(str(goal_lvl))
    if goal_cost is None:
        return GrimCalcResult(error=f"No data available for goal level {goal_lvl}")

    current_cost = cost_data.get(str(current_lvl)) if current_lvl is not None else None
    if current_lvl is not None and current_cost is None:
        return GrimCalcResult(error=f"No data available for current level {current_lvl}")

    essence_diff = 0
    imprint_diff = 0

    if isinstance(goal_cost, int):  # Enable book
        essence_goal = goal_cost
        essence_current = current_cost if current_cost is not None else 0
        essence_diff = essence_goal - essence_current
    else:  # Imprint book
        essence_goal = goal_cost.get("essence", 0)
        imprint_goal = goal_cost.get("imprint", 0)
        essence_current = current_cost.get("essence", 0) if current_cost is not None else 0
        imprint_current = current_cost.get("imprint", 0) if current_cost is not None else 0
        essence_diff = essence_goal - essence_current
        imprint_diff = imprint_goal - imprint_current

    essence_choices, imprint_choices = _calculate_event_choices(essence=essence_diff, imprint=imprint_diff)

    return GrimCalcResult(
        essence_cost=essence_diff,
        imprint_cost=imprint_diff,
        essence_choices=essence_choices,
        imprint_choices=imprint_choices
    )
