import nextcord
from typing import cast, Optional
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from src.utils.config import config
from src.utils.permissions import can_member_manage_messages


class DeleteMessage(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @nextcord.slash_command(
        name="delete_msg",
        description="Delete a message by ID",
    )
    async def delete_msg(
        self,
        interaction: Interaction,
        message_id: str = SlashOption(description="Message ID or message link to delete", required=True)
    ) -> None:
        user_id = getattr(interaction.user, "id", None)
        member = None
        if isinstance(interaction.user, nextcord.Member):
            member = interaction.user
        elif interaction.guild and user_id is not None:
            member = interaction.guild.get_member(user_id)

        # interaction.user can be Member, User, or None — use a safe cast for type-checkers
        is_owner = False
        user_obj = getattr(interaction, "user", None)
        if user_obj is not None:
            try:
                is_owner = await self.bot.is_owner(cast(nextcord.User, user_obj))
            except Exception:
                pass

        if member is None and not is_owner:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        if not can_member_manage_messages(member, is_owner):
            await interaction.response.send_message(
                "You do not have permission to use this command. Only server moderators and the bot owner may delete messages with this command.",
                ephemeral=True
            )
            return

        channel = getattr(interaction, "channel", None)
        if channel is None or not hasattr(channel, "fetch_message"):
            await interaction.response.send_message("Cannot identify the channel or fetch messages.", ephemeral=True)
            return

        # Normalize the input into an integer message ID (accept numeric ID or a full message link)
        def _parse_message_id(maybe_id: Optional[str]) -> Optional[int]:
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

        parsed_id = _parse_message_id(message_id)
        if parsed_id is None:
            await interaction.response.send_message("Invalid message ID or link — expected a numeric message id or a full message link.", ephemeral=True)
            return

        try:
            target = await channel.fetch_message(parsed_id)
        except Exception:
            await interaction.response.send_message("Message not found in this channel (check the message ID and channel).", ephemeral=True)
            return

        try:
            await target.delete()
            await interaction.response.send_message("Message deleted.", ephemeral=True)
        except Exception:
            await interaction.response.send_message("Failed to delete message (bot may lack delete permissions).", ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(DeleteMessage(bot))
