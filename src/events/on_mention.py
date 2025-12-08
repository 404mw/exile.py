"""
Event: on_message - react to bot mention
"""
import nextcord
from ..utils.config import emojis

def setup(bot):
    @bot.event
    async def on_message(message: nextcord.Message):
        # React with an emoji if the bot is mentioned
        if message.guild and bot.user and bot.user.mentioned_in(message):
            try:
                await message.add_reaction(emojis.blush_finger)
            except Exception:
                pass
        # Allow other commands/events to process
        await bot.process_commands(message)