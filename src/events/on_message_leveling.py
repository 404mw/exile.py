"""
Event: on_message - leveling system
Handles XP addition for user messages in the test server.
"""
import nextcord
from ..utils.config import config, channels, roles
from ..utils.functions.leveling import add_xp

def setup(bot):
    @bot.event
    async def on_message(message: nextcord.Message):
        """Handle leveling XP for user messages"""
        # Only process messages in the test server
        if not message.guild or message.guild.id != config.test_server_id:
            return
        
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Ignore spam channel
        if isinstance(message.channel, nextcord.TextChannel) and message.channel.name == channels.spam:
            return
        
        # Calculate XP multiplier based on exile role and chat
        xp_multiplier = 1
        
        # Check if user has exile role (message.author is a Member in guild context)
        has_exile_role = False
        if isinstance(message.author, nextcord.Member):
            has_exile_role = any(role.id == roles.exile_role for role in message.author.roles)
        
        # Check if message is in exile chat
        is_in_exile_chat = message.channel.id == channels.exile_chat
        
        # Apply multipliers: +1 for role, +1 for chat, x2 if both
        if has_exile_role and is_in_exile_chat:
            xp_multiplier = 2
        elif has_exile_role or is_in_exile_chat:
            xp_multiplier = 2  # +1 additional multiplier
        
        xp_amount = config.XP * xp_multiplier
        
        # Add XP and check for level up
        leveled_up, new_level, old_level = add_xp(
            message.author.id,
            message.author.name,
            xp_amount
        )
        
        # Send level up message if applicable
        if leveled_up:
            try:
                spam_channel = nextcord.utils.get(
                    message.guild.channels,
                    name=channels.level
                )
                
                if spam_channel and isinstance(spam_channel, nextcord.TextChannel):
                    level_up_message = (
                        f"{message.author.mention} has reached level **{new_level}**"
                    )
                    await spam_channel.send(level_up_message)
            except Exception as e:
                print(f"Error sending level up message: {e}")