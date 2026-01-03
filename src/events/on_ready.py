# -*- coding: utf-8 -*-

"""
This module handles the `on_ready` event, which is triggered when the bot
has successfully connected to Discord's API and is ready to start receiving
events.
"""

def setup(bot):
    """
    Set up the `on_ready` event listener.

    Args:
        bot: The `nextcord.ext.commands.Bot` instance.
    """
    @bot.event
    async def on_ready():
        """
        Announce that the bot has logged in and is ready.
        """
        # Print a confirmation message to the console to indicate that the bot
        # has successfully connected to Discord and is ready to operate.
        print(f"✅ Logged in as {bot.user}")