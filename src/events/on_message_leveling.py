# -*- coding: utf-8 -*-

"""
This module handles the `on_message` event for the leveling system.
It is responsible for granting XP to users based on their messages and
announcing level-ups when they occur.

The XP calculation is based on a four-tier system:
1.  **Static additions**: Flat bonuses for certain channels/roles.
2.  **Normal multipliers**: Multiplicative bonuses for certain channels/roles.
3.  **Level multiplier**: Bonus based on the user's current level.
4.  **True multiplier**: Final multiplier for a specific role.
"""

import nextcord
from ..utils.config import config, channels, emojis, user_ids
from ..utils.functions.leveling import add_xp, calculate_xp_from_context

def setup(bot):
    """
    Set up the `on_message` event listener for the leveling system.

    Args:
        bot: The `nextcord.ext.commands.Bot` instance.
    """
    @bot.event
    async def on_message(message: nextcord.Message):
        """
        Handles incoming messages to grant XP and process level-ups.

        This event handler performs the following checks:
        1.  Ensures the message is from the correct server (guild).
        2.  Ignores messages from bots or specific excluded users.
        3.  Ignores messages from designated spam or leveling channels.
        4.  Confirms the author is a `nextcord.Member` to access role information.

        If all checks pass, it calculates XP using the imported `calculate_xp_from_context`
        function, adds the XP to the user with `add_xp`, and sends a congratulatory
        message if the user levels up.

        Args:
            message: The `nextcord.Message` object representing the message that was sent.
        """
        # ============================================================================
        # PRE-PROCESSING CHECKS
        # ============================================================================

        # Only process messages within the designated server.
        if not message.guild or message.guild.id != config.exile_server_id:
            return

        # Ignore messages from bots or specified users to prevent XP farming.
        if message.author.bot or message.author.id == user_ids.blank:
            return

        # Ignore messages in channels designated for spam or level-up announcements.
        if isinstance(message.channel, nextcord.TextChannel) and message.channel.name in (channels.spam, channels.level):
            return

        # Ensure the author is a Member object to access their roles.
        if not isinstance(message.author, nextcord.Member):
            return

        # ============================================================================
        # XP CALCULATION & LEVELING
        # ============================================================================

        # Calculate the final XP amount based on context (roles, channel, etc.).
        xp_amount, _ = calculate_xp_from_context(
            config.base_XP,
            message.author,
            message.channel.id,
            message.author.id
        )

        # Add the calculated XP to the user and check for a level-up.
        leveled_up, new_level, _ = add_xp(
            message.author.id,
            message.author.name,
            xp_amount
        )

        # ============================================================================
        # LEVEL-UP ANNOUNCEMENT
        # ============================================================================

        # If the user has leveled up, send a public announcement.
        if leveled_up:
            try:
                # Find the designated channel for level-up messages.
                spam_channel = nextcord.utils.get(
                    message.guild.channels,
                    name=channels.level
                )

                # Send the congratulatory message.
                if spam_channel and isinstance(spam_channel, nextcord.TextChannel):
                    level_up_message = (
                        f"{emojis.party_shake} {message.author.mention} has reached level **{new_level}**"
                    )
                    await spam_channel.send(level_up_message)
            except Exception as e:
                # Silently ignore any exceptions that may occur, such as when the
                # bot does not have permission to send messages.
                print(f"Error sending level up message: {e}")
