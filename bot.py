# -*- coding: utf-8 -*-

"""
This file serves as the main entry point for the Exile.py Discord bot.

The bot is designed to be modular and scalable, with a clear separation of concerns.
This file is responsible for loading the environment variables, configuring the bot's
intents, and loading all the cogs from the `src`, `events`, and `message_commands` directories.

The bot's architecture is based on the following principles:
-   **Modularity**: Commands, events, and other features are organized into
    self-contained cogs, making it easy to add new features without
    affecting existing ones.
-   **Configurability**: The bot uses a centralized configuration system in
    `src/utils/config.py`, which allows for easy customization of the bot's
    behavior.
-   **Scalability**: The bot is designed to be scalable, with a clear project
    structure and a modular design that allows for future expansion.

This file is the central hub of the bot, bringing together all the different
components and running them as a cohesive application.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path to handle imports correctly
# This ensures imports work regardless of where the script is run from
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Change working directory to project root
# This ensures relative file paths (like data/awaPool.json) work correctly
os.chdir(project_root)

import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
from src.utils.config import config

# ======================================================================================
# ENVIRONMENT VARIABLES
# ======================================================================================

# Load environment variables from the .env file.
load_dotenv()

# Retrieve the bot token from the environment variables.
# The token is required for the bot to connect to Discord's API.
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("Bot token not found in environment variables")
print("Bot token acquired")

# ======================================================================================
# BOT CONFIGURATION
# ======================================================================================

# Configure the bot's intents, which determine which events the bot will receive.
# The `message_content` intent is required for the bot to read message content,
# which is used for message commands and other features.
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)

# ======================================================================================
# COG LOADING
# ======================================================================================

# Load all slash commands from the `src/slash_commands` directory.
# Each slash command is organized into its own cog, which is a self-contained
# class that can contain commands, event listeners, and state.
import src.slash_commands
src.slash_commands.setup(bot)

# Load all message commands from the `src/message_commands` directory.
# Message commands are context menu commands that can be triggered from a message.
from src.message_commands import msg_commands
msg_commands.setup(bot)

# Load all events from the `src/events` directory.
# Each event is in its own file, making it easy to manage and extend.
import src.events
src.events.setup(bot)

# =================================to======================================================
# BOT STARTUP
# ======================================================================================

# Run the bot with the configured token.
# This is the final step in the bot's startup process.
bot.run(TOKEN)
