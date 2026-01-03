# -*- coding: utf-8 -*-
"""
This module implements the `/imagine` slash command, which allows users to generate
images using DALL-E 3.
"""
import os
import nextcord
from nextcord.ext import commands
from openai import OpenAI
from src.utils.config import config
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")


class Imagine(commands.Cog):
    """
    A cog that handles the `/imagine` slash command.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize the Imagine cog.
        Args:
            bot (commands.Bot): The bot instance this cog is being added to.
        """
        self.bot = bot
        self.openai_client = OpenAI(api_key=API_KEY)

    @nextcord.slash_command(
        name="imagine",
        description="Generate an image using AI.",
        guild_ids=[config.test_server_id]
    )
    @commands.is_owner()
    async def imagine(
        self,
        interaction: nextcord.Interaction,
        prompt: str = nextcord.SlashOption(
            name="prompt",
            description="The prompt for the image generation.",
            required=True
        ),
    ):
        """
        Handle the `/imagine` slash command.
        Args:
            interaction (Interaction): The interaction object.
            prompt (str): The user's prompt.
        """
        await interaction.response.defer()

        try:
            response = self.openai_client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            await interaction.followup.send(image_url)

        except Exception as e:
            print(e)
            await interaction.followup.send(
                "⚠️ Something went wrong, kindly try again.", ephemeral=True
            )


def setup(bot: commands.Bot):
    """
    Set up the Imagine cog.
    Args:
        bot (commands.Bot): The bot instance to add the cog to.
    """
    bot.add_cog(Imagine(bot))
