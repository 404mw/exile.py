# -*- coding: utf-8 -*-
"""Tool for awakening simulation."""
from agents import function_tool
from src.utils.functions.awaken import make_response as _get_awakening_simulation

awakening_simulation = function_tool(
    _get_awakening_simulation,
    name_override="awakening_simulation",
    description_override="""
Simulates awakening a specified number of times and returns the results,
including CSG spent, retired amount, and gala points earned.

Args:
    iterations (int, required): The number of awakenings to simulate.

Returns:
    str: A formatted string summarizing the simulation results.
    """,
    use_docstring_info=False,
)
