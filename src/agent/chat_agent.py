"""
Chat Agent Module.
Implements a conversational AI agent using the OpenAI API.
This agent handles general chat interactions and provides helpful
but slightly sarcastic responses.
"""

import os
from agents import Agent, ModelSettings
from dotenv import load_dotenv

# Load environment variables for OpenAI model
load_dotenv()
MODEL = os.getenv("OPENAI_MODEL")

chat_agent = Agent(
    name = "Chat Agent",
    instructions = "You are a helpfull and sarcastic discord bot. Plain string no markdown",
    model = MODEL,
    model_settings = ModelSettings(max_tokens=200)
)