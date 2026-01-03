# -*- coding: utf-8 -*-

"""
This module implements the `/create_role` slash command, which allows bot owners
to create new roles in the server.
"""

import nextcord
from nextcord import Interaction, SlashOption, Color
from nextcord.ext import commands
from ..utils.config import config


class CreateRole(commands.Cog):
    """
    A cog that handles the `/create_role` slash command.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize the CreateRole cog.

        Args:
            bot (commands.Bot): The bot instance this cog is being added to.
        """
        self.bot = bot

    @nextcord.slash_command(
        name="create_role",
        description="Create a new role with default permissions.",
        guild_ids=[config.exile_server_id]
    )
    @commands.is_owner()
    async def create_role(
        self,
        interaction: Interaction,
        name: str = SlashOption(description="Name of the role"),
        color: str = SlashOption(description="Color of the role (hex format, e.g., 588543)")
    ):
        """
        Handle the `/create_role` slash command.

        Args:
            interaction (Interaction): The interaction object.
            name (str): The name of the role.
            color (str): The color of the role in hex format.
        """
        try:
            # ============================================================================
            # PRE-PROCESSING CHECKS
            # ============================================================================

            # Ensure we're in a guild.
            if not interaction.guild:
                await interaction.response.send_message(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return

            # ============================================================================
            # COMMAND PROCESSING
            # ============================================================================

            # Parse color from hex string.
            try:
                color_int = int(color.replace("#", ""), 16)
                role_color = Color(color_int)
            except ValueError:
                await interaction.response.send_message(
                    "Invalid color format. Please use hex format (e.g., 588543 or #588543).",
                    ephemeral=True,
                )
                return

            # Create the role with default permissions.
            new_role = await interaction.guild.create_role(
                name=name,
                color=role_color,
                reason=f"Created by {interaction.user}"
            )

            # ============================================================================
            # RESPONSE
            # ============================================================================

            await interaction.response.send_message(
                f"✅ Role `{new_role.name}` created successfully with color `#{color.replace('#', '').upper()}`.",
                ephemeral=True,
            )

        except nextcord.Forbidden:
            # ============================================================================
            # ERROR HANDLING
            # ============================================================================

            await interaction.response.send_message(
                "❌ I don't have permission to create roles in this server.",
                ephemeral=True,
            )
        except Exception:
            await interaction.response.send_message(
                "❌ An error occurred. Try again.",
                ephemeral=True,
            )


def setup(bot: commands.Bot):
    """
    Set up the CreateRole cog.

    Args:
        bot (commands.Bot): The bot instance to add the cog to.
    """
    bot.add_cog(CreateRole(bot))
