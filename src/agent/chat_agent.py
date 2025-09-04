import os
from agents import Agent, ModelSettings
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OPENAI_MODEL")

chat_agent = Agent(
    name = "Chat Agent",
    instructions = "You are a helpfull and sarcastic discord bot",
    model = MODEL,
    model_settings = ModelSettings(max_tokens=300)
)