# -*- coding: utf-8 -*-

"""
This module implements the navigator agent for the Exile.py bot.
The navigator agent acts as a traffic controller for user queries, directing
them to the appropriate agent for handling.

The navigator uses a simple classification system to determine whether a query
is a general question or a game-related query. Based on this classification,
it hands off the query to either the `chat_agent` or the `tool_agent`.
"""

import sys, os
from dotenv import load_dotenv

# ======================================================================================
# ENVIRONMENT VARIABLES
# ======================================================================================

# Add the src directory to the system path to allow for absolute imports.
sys.path.append(os.path.abspath("src"))

# Load environment variables from the .env file.
# The `OPENAI_MODEL` environment variable is required for the agent to know which
# model to use for generating responses.
load_dotenv()
MODEL = os.getenv("OPENAI_MODEL")