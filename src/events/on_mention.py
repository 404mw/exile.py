"""
Event: on_message - react to bot mention
"""
import nextcord
from ..utils.config import emojis

def setup(bot):
    @bot.event
    async def on_message(message: nextcord.Message):
        """React to bot mentions with an emoji"""
        # React with an emoji if the bot is mentioned
        if message.guild and bot.user and bot.user.mentioned_in(message):
            try:
                await message.add_reaction(emojis.blush_finger)
            except Exception:
                pass