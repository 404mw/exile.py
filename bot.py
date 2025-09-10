import os
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Import bot token
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Bot token not found in environment variables")
print("Bot token acquired")

intents = nextcord.Intents.default()
intents.message_content = True
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
