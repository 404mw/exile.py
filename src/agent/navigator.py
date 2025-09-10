"""
Navigator Agent Module.
This agent acts as a traffic controller for user queries,
directing them to either the tool_agent (for game-specific queries)
or chat_agent (for general conversation).

The navigator uses a simple classification system to determine
which agent should handle the user's request.
"""

import sys, os
sys.path.append(os.path.abspath("src"))
from agents import Agent, Runner
from dotenv import load_dotenv
from agent.tool_caller import tool_agent
from agent.chat_agent import chat_agent

# Load environment variables for model configuration
load_dotenv()
MODEL = os.getenv("OPENAI_MODEL")

nav_agent = Agent(
    name = "Navigator Agent",
    instructions = """
1- Do not answer queries yourself.
2- Classify each query:
  - If it’s a general question, handoff to chat_agent.
  - If it’s game-related data, handoff to tool_caller.
3- Always route, never respond directly.
""",
    handoffs = [tool_agent, chat_agent]
)

# response = Runner.run_sync(nav_agent, input="can you tell me what would be the SE HP for boss 145")
# print("---------------------------------------------")
# print(response.final_output)