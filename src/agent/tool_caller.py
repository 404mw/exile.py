import sys, os
sys.path.append(os.path.abspath("src"))
from agents import Agent, Runner, function_tool, ModelSettings
from utils.functions import get_se_hp as _get_se_hp
from utils.functions import get_dt_calc as _get_dt_calc
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OPENAI_MODEL")

# ----------------------- Tools -----------------------
se_hp = function_tool(
    _get_se_hp,
    name_override = "se_hp_getter",
    description_override = """
Compute the HP value of a Star Expedition (SE) boss.

Args:
    hp (int, required): Boss stage number (1–200).

    percentage (int, optional): Boss’s remaining HP %.

Returns:
    str: The calculated boss HP.
    """,
    use_docstring_info = False
)

temple_info = function_tool(
    _get_dt_calc,
    name_override = "temple_info_and_calculation",
    description_override = """
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
    use_docstring_info = False
)

# ----------------------- Agent -----------------------
tool_agent = Agent(
    name = "Tool Caller",
    instructions = "You must only use the tools provided to you—never handle requests on your own. If a tool doesn’t exist, tell the user (with light sarcasm) to just Google it. When a tool gives a response, that response is the final answer—don’t add extra calculations or commentary. \nPlain string no markdown",
    model = MODEL,
    tools = [se_hp, temple_info],
    model_settings = ModelSettings(max_tokens=600)
)

# response = Runner.run_sync(tool_agent, input="im about to reach temple level 10. i have 1x origin, 1x chaos, 20 gems and 400k spiritveins, what else do i need?")
# print(response)