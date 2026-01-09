# -*- coding: utf-8 -*-

"""
This module implements the tool-calling agent for the Exile.py bot.

The agent is responsible for handling game-specific queries by calling the
appropriate tools. It is designed to be a tool-user only and will not
handle any other queries.
"""

import os
from agents import Agent, ModelSettings
from dotenv import load_dotenv

from src.agent.tools import (
    se_hp,
    temple_info,
    awakening_simulation,
    grimoire_calculation,
)

# ======================================================================================
# ENVIRONMENT VARIABLES
# ======================================================================================

# Load environment variables from the .env file.
# The `OPENAI_MODEL` environment variable is required for the agent to know which
# model to use for generating responses.
load_dotenv()
MODEL = os.getenv("OPENAI_MODEL")

# ======================================================================================
# AGENT CONFIGURATION
# ======================================================================================

# Create an instance of the `Agent` class, which will be used to handle tool-calling
# queries. The agent's behavior is defined by the `instructions` parameter, which
# tells the agent to only use the tools provided and to not handle any other queries.
tool_agent = Agent(
    name="Tool Caller",
    instructions="You must only use the tools provided to you—never handle requests on your own. If a tool doesn’t exist, refuse politly.\nPlain string no markdown",
    model=MODEL,
    tools=[se_hp, temple_info, awakening_simulation, grimoire_calculation],
    tool_use_behavior="stop_on_first_tool",
    model_settings=ModelSettings(max_tokens=300),
)