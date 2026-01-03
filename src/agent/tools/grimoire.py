# -*- coding: utf-8 -*-
"""Tool for Grimoire upgrade cost calculation."""
from agents import function_tool
from src.utils.config import emojis
from src.utils.functions.grim_calc import (
    get_grim_calc as _get_grim_calc_data,
    GrimCalcResult,
)


def _get_grim_calc_response(book: str, goal_lvl: int, current_lvl: int | None = None) -> str:
    """Formats the Grimoire calculation result into a string."""
    result = _get_grim_calc_data(book, goal_lvl, current_lvl)

    if result.error:
        return f"⚠️ {result.error}"

    if book.lower() == "enable":
        book_name = f"{emojis.grim_book1} Grimoire • Enabling Chapter"
        level_range = f"`{current_lvl} → {goal_lvl}`" if current_lvl else f"`→ {goal_lvl}`"
        response = (
            f"> **{book_name}** {level_range}\n"
            f"> \n"
            f"> {emojis.grim_essence} `{result.essence_cost:,}` {result.essence_choices:.2f} event choices"
        )
    else:  # Imprint
        book_name = "Grimoire • Imprint Chapter"
        level_range = f"`{current_lvl} → {goal_lvl}`" if current_lvl else f"`→ {goal_lvl}`"
        response = (
            f"> **{book_name}** {level_range}\n"
            f"> \n"
            f"> {emojis.grim_essence} `{result.essence_cost:,}` {result.essence_choices:.2f} event choices\n"
            f"> {emojis.grim_imprint} `{result.imprint_cost:,}` {result.imprint_choices:.2f} event choices"
        )
    return response


grimoire_calculation = function_tool(
    _get_grim_calc_response,
    name_override="grimoire_calculation",
    description_override="""
Calculates the resource cost to upgrade a Grimoire from a current level
to a target level.

Args:
    book (str, required): The type of Grimoire ("Enable" or "Imprint").
    goal_lvl (int, required): The target level for the calculation (1-150).
    current_lvl (int, optional): The current grimoire level (1-150).

Returns:
    str: A formatted string with the calculated resource costs.
    """,
    use_docstring_info=False,
)
