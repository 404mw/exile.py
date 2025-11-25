"""
Event: on_message - react to bot mention
"""
import nextcord

def setup(bot):
    @bot.event
    async def on_message(message: nextcord.Message):
        # React with an emoji if the bot is mentioned
        if message.guild and bot.user and bot.user.mentioned_in(message):
            try:
                await message.add_reaction("<:blush_finger:1337833082954317885>")
            except Exception:
                pass
        # Allow other commands/events to process
        await bot.process_commands(message)