import os
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Import bot token
try:
    TOKEN = (os.getenv("TOKEN"))
    print("Bot token acquired")
except Exception as e:
    print(f"Bot token not found\n\n{e}")

intents = nextcord.Intents.default()
bot = commands.Bot(intents=intents)

# Load slash commands
import src.slash_commands
src.slash_commands.setup(bot)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

bot.run((TOKEN))
