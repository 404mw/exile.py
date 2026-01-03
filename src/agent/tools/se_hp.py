# -*- coding: utf-8 -*-
"""Tool to compute the HP value of a Star Expedition (SE) boss."""
from agents import function_tool
from src.utils.functions import get_se_hp as _get_se_hp

se_hp = function_tool(
    _get_se_hp,
    name_override="se_hp_getter",
    description_override="""
Compute the HP value of a Star Expedition (SE) boss.

Args:
    hp (int, required): Boss stage number (1–200).

    percentage (int, optional): Boss’s remaining HP %.

Returns:
    int: The calculated boss HP.
    """,
    use_docstring_info=False,
)
