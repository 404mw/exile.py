import nextcord
from nextcord.ext import commands
from src.utils.functions.reload_config import reload_msg_commands
from src.utils.config import config


class Reload(commands.Cog):
    """
    Reload Command Cog.
    Provides a slash command to reload message commands configuration.
    Restricted to bot owner only.
    """
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Reload cog.
        
        Args:
            bot (commands.Bot): The bot instance this cog is being added to
        """
        self.bot = bot

    @nextcord.slash_command(
        name="reload_cmd",
        description="Reload message commands configuration",
        guild_ids=[config.test_server_id]
    )
    @commands.is_owner()  # Only bot owner can use this command
    async def reload(self, interaction: nextcord.Interaction):
        """Reload message commands configuration without restarting the bot."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            if reload_msg_commands(self.bot):
                await interaction.followup.send(
                    "✅ Message commands reloaded successfully!",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "❌ Failed to reload message commands. Check console for details.",
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )


def setup(bot: commands.Bot):
    bot.add_cog(Reload(bot))