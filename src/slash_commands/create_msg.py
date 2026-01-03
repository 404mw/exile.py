# -*- coding: utf-8 -*-

"""
This module implements the `/create_msg` slash command, which allows bot owners
and server moderators to send messages as the bot.
"""

from typing import cast, Optional
import nextcord
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from src.utils.config import config
from src.utils.permissions import can_member_manage_messages


class CreateMessage(commands.Cog):
    """
    A cog that handles the `/create_msg` slash command.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """
        Initialize the CreateMessage cog.

        Args:
            bot (commands.Bot): The bot instance this cog is being added to.
        """
        self.bot = bot

    @nextcord.slash_command(
        name="create_msg",
        description="Send a message as Exile.bot",
    )
    async def create_msg(
        self,
        interaction: Interaction,
        content: str = SlashOption(description="The message content", required=True),
        channel: Optional[nextcord.TextChannel] = SlashOption(
            description="Channel to send the message in (defaults to current channel)",
            required=False,
            default=None,
        ),
        reply_to: Optional[str] = SlashOption(
            description="Message ID (or link) to reply to", required=False, default=None
        ),
    ) -> None:
        """
        Handle the `/create_msg` slash command.

        Args:
            interaction (Interaction): The interaction object.
            content (str): The message content.
            channel (Optional[nextcord.TextChannel]): The channel to send the message in.
            reply_to (Optional[str]): The message ID or link to reply to.
        """
        # ============================================================================
        # PERMISSION CHECKS
        # ============================================================================

        # Resolve member and check owner/mod permissions.
        user_id = getattr(interaction.user, "id", None)
        member = None
        if isinstance(interaction.user, nextcord.Member):
            member = interaction.user
        elif interaction.guild and user_id is not None:
            member = interaction.guild.get_member(user_id)

        is_owner = False
        user_obj = getattr(interaction, "user", None)
        if user_obj is not None:
            try:
                is_owner = await self.bot.is_owner(cast(nextcord.User, user_obj))
            except Exception:
                pass

        if member is None and not is_owner:
            await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
            return

        if not can_member_manage_messages(member, is_owner):
            await interaction.response.send_message(
                "You do not have permission to use this command. Only server moderators and the bot owner may create messages with this command.",
                ephemeral=True,
            )
            return

        # ============================================================================
        # COMMAND PROCESSING
        # ============================================================================

        # Choose the channel where the command was invoked, or use the provided channel.
        target_channel = (
            channel if channel is not None else getattr(interaction, "channel", None)
        )
        if target_channel is None or not hasattr(target_channel, "send"):
            await interaction.response.send_message(
                "Cannot identify the target channel for the message.", ephemeral=True
            )
            return

        # Defer the response to allow time for the bot to process the command.
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            pass

        # ============================================================================
        # HELPER FUNCTIONS
        # ============================================================================

        def _parse_message_id(maybe_id: Optional[str]) -> Optional[int]:
            """
            Normalize a user-supplied message ID/link into an int.
            """
            if maybe_id is None:
                return None
            maybe_id = maybe_id.strip()
            if "/" in maybe_id:
                try:
                    maybe_id = maybe_id.rstrip("/").split("/")[-1]
                except Exception:
                    pass
            maybe_id = maybe_id.strip("<>")
            if not maybe_id.isdigit():
                return None
            try:
                return int(maybe_id)
            except Exception:
                return None

        async def _send_response(text: str, *, ephemeral: bool = True) -> None:
            """
            Send a response to the interaction, either as a new message or a
            follow-up.
            """
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(text, ephemeral=ephemeral)
                else:
                    await interaction.followup.send(text, ephemeral=ephemeral)
            except Exception:
                try:
                    if interaction.response.is_done():
                        await interaction.response.send_message(text, ephemeral=ephemeral)
                    else:
                        await interaction.followup.send(text, ephemeral=ephemeral)
                except Exception:
                    pass

        # ============================================================================
        # RESPONSE HANDLING
        # ============================================================================

        sent = None
        if reply_to is not None:
            parsed_id = _parse_message_id(reply_to)
            if parsed_id is None:
                await _send_response(
                    "Invalid message ID or link provided; expected a numeric message ID or message link."
                )
            else:
                try:
                    orig = await target_channel.fetch_message(parsed_id)
                    sent = await orig.reply(content)
                except Exception:
                    try:
                        sent = await target_channel.send(content)
                    except Exception:
                        sent = None
        else:
            try:
                sent = await target_channel.send(content)
            except Exception:
                sent = None

        if sent is not None:
            await _send_response("Message created.")
        else:
            await _send_response(
                "Failed to create message (bot may lack send permissions)."
            )


def setup(bot: commands.Bot) -> None:
    """
    Set up the CreateMessage cog.

    Args:
        bot (commands.Bot): The bot instance to add the cog to.
    """
    bot.add_cog(CreateMessage(bot))
