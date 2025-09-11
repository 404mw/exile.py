"""
Discord Bot - Server Listing Utility

This script connects to Discord using Nextcord, authenticates with a bot token
(from the .env file), and prints out a list of all servers (guilds) the bot is 
currently in. After listing the servers, the bot closes automatically.

Environment Variables:
- TOKEN: Discord bot token (stored in .env file)

Usage:
1. Add your bot token to a `.env` file as TOKEN=your_token_here
2. Run the script: uv run scripts/server_names.py
3. The bot will log in, print the servers it belongs to, and then exit.
"""


import os
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# --- CONFIG ---
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("Bot token not found")
# --------------

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print("The bot is in the following servers:")
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")

    await bot.close()

bot.run(TOKEN)
