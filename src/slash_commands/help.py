import nextcord
from nextcord.ext import commands
from src.utils.config import config


class Help(commands.Cog):
    """
    Help Command Cog.
    Provides a slash command to display all available commands with descriptions.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize the Help cog.

        Args:
            bot (commands.Bot): The bot instance this cog is being added to
        """
        self.bot = bot

    @nextcord.slash_command(
        name="help",
        description="Show all available commands"
    )
    async def help(self, interaction: nextcord.Interaction):
        """
        Display an embed with all available slash commands and their descriptions.

        Args:
            interaction (nextcord.Interaction): The interaction object from Discord
        """
        try:
            # Create embed
            embed = nextcord.Embed(
                title="Available Commands",
                description="All the active **/commands** are listed here:",
                color=0x588543
            )
            
            # Set bot's avatar as thumbnail
            if self.bot.user and self.bot.user.avatar:
                embed.set_thumbnail(url=self.bot.user.avatar.url)

            # Define commands and descriptions
            commands_data = [
                {
                    "name": "`/ping`",
                    "description": "> Check the bot's latency"
                },
                {
                    "name": "`/dice`",
                    "description": "> Roll a dice with configurable sides"
                },
                {
                    "name": "`/ask`",
                    "description": "> Ask a general or Idle Heroes related question (AI-powered)"
                },
                {
                    "name": "`/dt_calc`",
                    "description": "> Calculate Destiny Transition upgrade costs"
                },
                {
                    "name": "`/grim_calc`",
                    "description": "> Calculate Grimoire upgrade costs with event choice equivalents"
                },
                {
                    "name": "`/awaken`",
                    "description": "> Simulate hero awakenings and calculate costs"
                },
                {
                    "name": "`/se`",
                    "description": "> Calculate Star Expedition boss HP at different levels"
                },
                {
                    "name": "`/giveaway`",
                    "description": "> Create and manage giveaways"
                }
            ]

            # Add fields to embed
            for cmd in commands_data:
                embed.add_field(
                    name=cmd["name"],
                    value=cmd["description"],
                    inline=False
                )

            # Add footer
            embed.set_footer(text="Use /help to see this message anytime")

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(
                "⚠️ Something went wrong while generating help",
                ephemeral=True
            )
            print(f"Error in help command: {e}")


def setup(bot: commands.Bot):
    bot.add_cog(Help(bot))
