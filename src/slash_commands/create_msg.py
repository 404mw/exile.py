import nextcord
from typing import cast, Optional
from nextcord import Interaction, SlashOption
from nextcord.ext import commands

from src.utils.config import config
from src.utils.permissions import can_member_manage_messages


class CreateMessage(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @nextcord.slash_command(
        name="create_msg",
        description="Send a message as Exile.bot",
    )
    async def create_msg(
        self,
        interaction: Interaction,
        content: str = SlashOption(description="The message content", required=True),
        channel: Optional[nextcord.TextChannel] = SlashOption(description="Channel to send the message in (defaults to current channel)", required=False, default=None),
        reply_to: Optional[str] = SlashOption(description="Message ID (or link) to reply to", required=False, default=None)
    ) -> None:
        # resolve member and check owner/mod permissions
        user_id = getattr(interaction.user, "id", None)
        member = None
        if isinstance(interaction.user, nextcord.Member):
            member = interaction.user
        elif interaction.guild and user_id is not None:
            member = interaction.guild.get_member(user_id)

        # interaction.user can be a Member, User, or None. is_owner expects a User type,
        # so do a safe check / cast before calling bot.is_owner to satisfy type checkers.
        is_owner = False
        user_obj = getattr(interaction, "user", None)
        if user_obj is not None:
            try:
                # cast to nextcord.User to satisfy the type-checker (Member is compatible at runtime)
                is_owner = await self.bot.is_owner(cast(nextcord.User, user_obj))
            except Exception:
                pass

        if member is None and not is_owner:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return

        if not can_member_manage_messages(member, is_owner):
            await interaction.response.send_message(
                "You do not have permission to use this command. Only server moderators and the bot owner may create messages with this command.",
                ephemeral=True
            )
            return

        # choose the channel where the command was invoked, or use the provided channel
        target_channel = channel if channel is not None else getattr(interaction, "channel", None)
        if target_channel is None or not hasattr(target_channel, "send"):
            await interaction.response.send_message("Cannot identify the target channel for the message.", ephemeral=True)
            return

        # We may need to defer if we perform multiple API calls
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            pass

        # Helper: normalize a user-supplied message id / link / mention into an int
        def _parse_message_id(maybe_id: Optional[str]) -> Optional[int]:
            if maybe_id is None:
                return None
            maybe_id = maybe_id.strip()
            # if user pasted a full message URL, take the last path segment
            if "/" in maybe_id:
                try:
                    maybe_id = maybe_id.rstrip("/").split("/")[-1]
                except Exception:
                    pass
            # remove angle brackets or mention-like wrappers
            maybe_id = maybe_id.strip("<>")
            if not maybe_id.isdigit():
                return None
            try:
                return int(maybe_id)
            except Exception:
                return None

        # helper to send a reply or followup depending on whether the interaction
        # has already been responded to/deferred. Using response.followup before
        # an initial response causes 'The application did not respond' errors.
        async def _send_response(text: str, *, ephemeral: bool = True) -> None:
            try:
                # prefer response.send_message when no initial response has been done
                if not interaction.response.is_done():
                    await interaction.response.send_message(text, ephemeral=ephemeral)
                else:
                    await interaction.followup.send(text, ephemeral=ephemeral)
            except Exception:
                # try the other method as a last resort
                try:
                    if interaction.response.is_done():
                        await interaction.response.send_message(text, ephemeral=ephemeral)
                    else:
                        await interaction.followup.send(text, ephemeral=ephemeral)
                except Exception:
                    # swallow — we can't do more at this point
                    pass

        # If reply target provided, try to fetch the message and reply
        sent = None
        if reply_to is not None:
            parsed_id = _parse_message_id(reply_to)
            if parsed_id is None:
                # invalid ID format — respond back to user
                await _send_response("Invalid message ID or link provided; expected a numeric message ID or message link.")
                # bail out — not an error to continue, leave sent as None
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
            await _send_response("Failed to create message (bot may lack send permissions).")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(CreateMessage(bot))
