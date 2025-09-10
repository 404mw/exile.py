"""
A Discord bot for Idle Heroes (IH) game-related features and utilities.
The bot provides various commands for game calculations, awakenings simulation,
and other helper functions.
"""

import os
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import and validate bot token
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Bot token not found in environment variables")
print("Bot token acquired")

# Configure bot intents
intents = nextcord.Intents.default()
intents.message_content = True  # Enable message content intent for message commands
bot = commands.Bot(intents=intents)

# Load slash commands
import src.slash_commands
src.slash_commands.setup(bot)

# Load message commands
from src.message_commands import msg_commands
msg_commands.setup(bot)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

bot.run(TOKEN)
