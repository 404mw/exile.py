import nextcord
from nextcord.ext import commands
from src.utils.functions.reload_config import reload_all
from src.utils.config import config


class ReloadAll(commands.Cog):
    """
    ReloadAll Command Cog.
    Provides a slash command to reload all bot modules and cogs.
    Restricted to bot owner only.
    """
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the ReloadAll cog.
        
        Args:
            bot (commands.Bot): The bot instance this cog is being added to
        """
        self.bot = bot

    @nextcord.slash_command(
        name="reload_all",
        description="Reload all bot modules, cogs, and configurations",
        guild_ids=[config.test_server_id]
    )
    @commands.is_owner()  # Only bot owner can use this command
    async def reload_all_cmd(self, interaction: nextcord.Interaction):
        """Reload all bot modules, cogs, and configurations without restarting the bot."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            success, report = reload_all(self.bot)
            
            # Format the report message
            msg = []
            if report["success"]:
                msg.append("✅ Successfully reloaded:")
                msg.extend(f"  • {item}" for item in report["success"])
            
            if report["failed"]:
                if msg:
                    msg.append("\n❌ Failed to reload:")
                else:
                    msg.append("❌ Failed to reload:")
                msg.extend(f"  • {item}" for item in report["failed"])
            
            await interaction.followup.send(
                "\n".join(msg),
                ephemeral=True
            )
                
        except Exception as e:
            await interaction.followup.send(
                f"❌ A critical error occurred: {str(e)}",
                ephemeral=True
            )


def setup(bot: commands.Bot):
    bot.add_cog(ReloadAll(bot))