"""
Event: on_message - leveling system
Handles XP addition for user messages in the test server.
Uses the four-tier XP calculation system:
1. Static additions: flat bonuses for certain channels/roles
2. Normal multipliers: multiplicative bonuses for certain channels/roles
3. Level multiplier: bonus based on user's current level
4. True multiplier: final multiplier for a specific role
"""
import nextcord
from ..utils.config import config, channels, emojis, user_ids
from ..utils.functions.leveling import add_xp, calculate_xp_from_context

def setup(bot):
    @bot.event
    async def on_message(message: nextcord.Message):
        """Handle leveling XP for user messages"""
        # Only process messages in the test server
        if not message.guild or message.guild.id != config.exile_server_id:
            return
        
        # Ignore bot and blank's messages
        if message.author.bot or message.author.id == user_ids.blank:
            return
        
        # Ignore spam channel
        if isinstance(message.channel, nextcord.TextChannel) and message.channel.name in (channels.spam, channels.level):
            return
        
        # User must be a Member to have roles
        if not isinstance(message.author, nextcord.Member):
            return
        
        # Calculate XP using the four-tier system
        xp_amount, breakdown = calculate_xp_from_context(
            config.base_XP,
            message.author,
            message.channel.id,
            message.author.id
        )
        
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
                        f"{emojis.party_shake} {message.author.mention} has reached level **{new_level}**"
                    )
                    await spam_channel.send(level_up_message)
            except Exception as e:
                print(f"Error sending level up message: {e}")
