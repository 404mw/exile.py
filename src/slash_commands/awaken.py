# -*- coding: utf-8 -*-

"""
This module implements the `/awaken` slash command, which allows users to
simulate hero awakenings with different probability pools (normal or buffed)
and calculate the total resources spent and gained.
"""

import nextcord
from nextcord.ext import commands

from src.utils.functions.awaken import make_response
from src.utils.config import channels


class Awaken(commands.Cog):
    """
    A cog that handles the `/awaken` slash command.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize the Awaken cog.

        Args:
            bot (commands.Bot): The bot instance this cog is being added to.
        """
        self.bot = bot

    @nextcord.slash_command(
        name="awaken",
        description="Awakenings Simulation"
    )
    async def awaken(
        self,
        interaction: nextcord.Interaction,
        times: int = nextcord.SlashOption(
            name="times",
            description="Number of times to awaken",
            required=True,
            min_value=1,
            max_value=999,
            default=1
        )
    ):
        """
        Handle the `/awaken` slash command.

        Args:
            interaction (Interaction): The interaction object.
            times (int): The number of times to awaken.
        """
        try:
            # ============================================================================
            # PRE-PROCESSING CHECKS
            # ============================================================================

            # Check whether the command is used in an allowed channel.
            allowed_channel = channels.spam
            if interaction.guild and isinstance(interaction.channel, nextcord.TextChannel):
                if interaction.channel.name != allowed_channel:
                    await interaction.response.send_message(
                        f"This command can only be used in the #{allowed_channel} channel.\n"
                        f"If it's not there, please create one.",
                        ephemeral=True
                    )
                    return

            # ============================================================================
            # COMMAND PROCESSING
            # ============================================================================

            # Generate the response for the awakening simulation.
            final_reply = make_response(times)

            # ============================================================================
            # RESPONSE
            # ============================================================================

            # Send the response to the user.
            await interaction.response.send_message(final_reply)

        except Exception as e:
            # ============================================================================
            # ERROR HANDLING
            # ============================================================================

            # Print the error to the console for debugging purposes.
            print(e)

            # Send an ephemeral error message to the user.
            await interaction.response.send_message("Something went wrong, kindly try again.", ephemeral=True)


def setup(bot: commands.Bot):
    """
    Set up the Awaken cog.

    Args:
        bot (commands.Bot): The bot instance to add the cog to.
    """
    bot.add_cog(Awaken(bot))
