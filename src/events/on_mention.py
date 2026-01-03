# -*- coding: utf-8 -*-

"""
This module handles the `on_message` event and reacts to bot mentions.
When the bot is mentioned in a message, it will react with an emoji to
acknowledge the mention.
"""

import nextcord
from ..utils.config import emojis

def setup(bot):
    """
    Set up the `on_message` event listener for bot mentions.

    Args:
        bot: The `nextcord.ext.commands.Bot` instance.
    """
    @bot.listen("on_message")
    async def _on_message_mention(message: nextcord.Message):
        """
        React to bot mentions with an emoji.

        Args:
            message: The `nextcord.Message` object representing the message.
        """
        # React with an emoji if the bot is mentioned in the message.
        # This provides a simple and friendly way to acknowledge the mention.
        if message.guild and bot.user and bot.user.mentioned_in(message):
            try:
                await message.add_reaction(emojis.blush_finger)
            except Exception:
                # Silently ignore any exceptions that may occur, such as when the
                # bot does not have permission to add reactions.
                pass