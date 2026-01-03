# -*- coding: utf-8 -*-

"""
This module implements a cog for handling message-based commands with a prefix.
It loads commands and their responses from a JSON file and responds to matching
messages.
"""

import json
import random
import re
from pathlib import Path

import nextcord
from nextcord.ext import commands

from src.utils.config import config


class MessageCommands(commands.Cog):
    """
    A cog that handles message-based commands with a prefix.
    It loads commands and their responses from a JSON file and responds to
    matching messages.

    Features:
    - Case-insensitive command matching.
    - Alias support for commands.
    - Media file responses (images/GIFs).
    - Random response selection if multiple responses exist.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize the MessageCommands cog.

        Args:
            bot (commands.Bot): The bot instance this cog is being added to.
        """
        self.bot = bot
        self.prefix = config.PREFIX
        self.commands_data = self.load_commands()

    def load_commands(self):
        """
        Load the commands.json file from the data directory.
        """
        json_path = Path(__file__).parent.parent.parent / "data" / "msgCommands.json"
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def normalize(self, text: str) -> str:
        """
        Lowercase and strip punctuation for matching.
        """
        return re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        """
        Listen for messages and respond to commands.

        Args:
            message (nextcord.Message): The message that was sent.
        """
        # ============================================================================
        # PRE-PROCESSING CHECKS
        # ============================================================================

        # Ignore bots (including itself).
        if message.author.bot:
            return

        # Check if the message starts with the bot's prefix.
        content = message.content
        if not content.startswith(self.prefix):
            return

        # ============================================================================
        # COMMAND PROCESSING
        # ============================================================================

        # Strip prefix and normalize input.
        command_text = self.normalize(content[len(self.prefix):])

        # Use lookup table to find command name from input (could be alias).
        lookup = self.commands_data.get("lookup", {})
        commands_dict = self.commands_data.get("commands", {})

        command_key = lookup.get(command_text)
        if not command_key or command_key not in commands_dict:
            return

        # ============================================================================
        # RESPONSE HANDLING
        # ============================================================================

        # Get the command and its responses.
        cmd = commands_dict[command_key]
        responses = cmd.get("responses", [])
        if responses:
            response = random.choice(responses)

            # Check if the response is a media file.
            if response.startswith("./media"):
                # Go up two levels from this file (src/messagecommand) → root/
                project_root = Path(__file__).resolve().parents[2]
                file_path = project_root / response[2:]  # strip "./" from response

                if file_path.exists():
                    await message.reply(file=nextcord.File(file_path))
                else:
                    print(f"[WARN] Media file not found: {file_path}")
            else:
                await message.reply(response)

            return  # Stop after the first match.


def setup(bot: commands.Bot):
    """
    Set up the MessageCommands cog.

    Args:
        bot (commands.Bot): The bot instance to add the cog to.
    """
    bot.add_cog(MessageCommands(bot))
