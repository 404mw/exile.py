# -*- coding: utf-8 -*-

"""
Diagnostic command to test interaction response times.
This helps identify if there are latency issues causing interaction timeouts.
"""

import nextcord
from nextcord.ext import commands
from src.utils.config import config
import time


class TestResponse(commands.Cog):
    """
    A diagnostic cog to test interaction response times.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="test_response",
        description="Test bot response time (diagnostic command)",
        guild_ids=[config.test_server_id]
    )
    async def test_response(self, interaction: nextcord.Interaction):
        """
        Test how quickly the bot can respond to an interaction.
        """
        start_time = time.time()

        try:
            # Try to defer immediately
            await interaction.response.defer()
            defer_time = time.time() - start_time

            # Send response with timing info
            await interaction.followup.send(
                f"✅ Response test successful!\n"
                f"⏱️ Defer took: {defer_time:.3f} seconds\n"
                f"🏓 Bot latency: {self.bot.latency * 1000:.0f}ms"
            )

        except nextcord.errors.NotFound as e:
            # Interaction expired before we could even defer
            elapsed = time.time() - start_time
            print(f"❌ Interaction expired! Took {elapsed:.3f}s to reach defer")
            print(f"Error: {e}")


def setup(bot: commands.Bot):
    """Set up the TestResponse cog."""
    bot.add_cog(TestResponse(bot))
