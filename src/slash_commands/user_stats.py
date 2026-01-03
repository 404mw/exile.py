import nextcord
from typing import cast
from src.utils.functions import format_relative_date
from nextcord import SlashOption
from nextcord.ext import commands
from src.utils.config import config
from src.utils.functions import fetch_user_level


class UserStats(commands.Cog):
    """
    Encapsulates the `/user_stats` command, providing a detailed overview of a user's server presence.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="user_stats",
        description="Show a user's complete stats",
        guild_ids=[config.exile_server_id]
    )
    async def user_stats(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.User = SlashOption(description="User to look up, defaults to yourself", required=False),
    ):
        """
        Displays a comprehensive summary of a user's statistics in the server.

        This command shows both general Discord info (username, ID, account creation date)
        and server-specific details (nickname, join date, roles, level, and XP).
        If no user is specified, it defaults to the user who invoked the command.

        Args:
            interaction: The `nextcord.Interaction` object representing the command invocation.
            user: An optional `nextcord.User` to look up. Defaults to the command user.
        """
        # If no user is specified, default to the user who initiated the command.
        target = user or interaction.user

        try:
            # Defer the response to allow time for data fetching.
            await interaction.response.defer()

            # Fetch the user's leveling information from the data file.
            info = fetch_user_level(target.id)
            if not info:
                await interaction.followup.send(f"No level data found for {target.mention}", ephemeral=True)
                return

            # ============================================================================
            # DATA EXTRACTION AND PREPARATION
            # ============================================================================
            
            # Extract leveling progress information from the fetched data.
            current_level = info.get("level", 0)
            total_xp = info.get("xp", 0)
            xp_progress = info.get("xp_progress", 0)
            xp_for_next_level = info.get("xp_for_next_level", 0)
            
            # Calculate the completion percentage for the current level.
            progress_percent = 0
            if xp_for_next_level > 0:
                progress_percent = int((xp_progress / xp_for_next_level) * 100)

            # ============================================================================
            # EMBED CREATION
            # ============================================================================
            
            embed = nextcord.Embed(
                title=f"{target.display_name}'s Stats",
                color=0x588543
            )

            # Set the embed thumbnail to the user's avatar.
            try:
                embed.set_thumbnail(url=target.display_avatar.url)
            except Exception:
                pass

            # ============================================================================
            # POPULATE EMBED - GENERAL DISCORD INFO
            # ============================================================================
            
            # Format the username, including the discriminator if it's not the new '0' default.
            discr = getattr(target, "discriminator", None)
            if discr and discr != "0":
                username = f"{getattr(target, 'name', str(target))}#{discr}"
            else:
                username = getattr(target, "name", str(target))

            # Format the account creation date to a relative time string.
            account_created = None
            try:
                account_created = format_relative_date(getattr(target, "created_at", None))
            except Exception:
                account_created = None

            embed.add_field(name="Username", value=username, inline=True)
            embed.add_field(name="ID", value=str(target.id), inline=True)
            embed.add_field(name="Bot", value=("Yes" if getattr(target, "bot", False) else "No"), inline=True)
            if account_created:
                embed.add_field(name="Account Created", value=account_created, inline=True)

            # ============================================================================
            # POPULATE EMBED - SERVER-SPECIFIC (MEMBER) INFO
            # ============================================================================

            # Check if the target is a full member object to get server-specific details.
            is_member = isinstance(target, nextcord.Member)
            if is_member:
                member = cast(nextcord.Member, target)

                # Get nickname, handling potential exceptions.
                try:
                    nick = member.nick or "-"
                except Exception:
                    nick = "-"

                # Format the server join date to a relative time string.
                joined = None
                try:
                    joined = format_relative_date(member.joined_at)
                except Exception:
                    joined = None

                # Get the top role and total role count.
                top_role_name = "-"
                roles_count = "-"
                try:
                    # Exclude @everyone from the role count for a more accurate number.
                    roles = [r for r in member.roles if getattr(r, "name", "") != "@everyone"]
                    roles_count = len(roles)
                    top_role = getattr(member, "top_role", None)
                    top_role_name = top_role.name if top_role else "-"
                except Exception:
                    roles_count = "-"
                    top_role_name = "-"

                embed.add_field(name="Nickname", value=nick, inline=True)
                if joined:
                    embed.add_field(name="Server Join Date", value=joined, inline=True)
                embed.add_field(name="Top Role", value=top_role_name, inline=True)
                embed.add_field(name="Roles Count", value=str(roles_count), inline=True)

            # ============================================================================
            # POPULATE EMBED - LEVELING INFO
            # ============================================================================

            embed.add_field(name="Server Level", value=str(current_level), inline=True)
            embed.add_field(name="Total XP", value=f"{total_xp:,}", inline=True)
            embed.add_field(
                name="Progress to Next Level",
                value=f"{xp_progress:,} / {xp_for_next_level:,} XP ({progress_percent}%)",
                inline=False,
            )

            # Send the completed embed.
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(e)
            # Gracefully handle any unexpected errors.
            if not interaction.response.is_done():
                await interaction.response.send_message("⚠️ Something went wrong", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ Something went wrong", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(UserStats(bot))
