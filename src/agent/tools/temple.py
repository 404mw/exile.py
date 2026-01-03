# -*- coding: utf-8 -*-
"""Tool to calculate the required resources for a specific temple level."""
from agents import function_tool
from src.utils.functions import get_dt_calc as _get_dt_calc

temple_info = function_tool(
    _get_dt_calc,
    name_override="temple_info_and_calculation",
    description_override="""
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
""",
    use_docstring_info=False,
)
