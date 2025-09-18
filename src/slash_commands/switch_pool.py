import nextcord
from nextcord.ext import commands
from src.utils.config import config
from src.utils.functions.reload_config import reload_all
import json
import os

class SwitchPool(commands.Cog):
    """
    Switch Command Cog.
    Provides a slash command to switch the value in awaPool.json.
    """
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Switch cog.
        
        Args:
            bot (commands.Bot): The bot instance this cog is being added to
        """
        self.bot = bot

    @nextcord.slash_command(
        name="switch_pool",
        description="Switchs the awaken pool (True for normal)",
        guild_ids=[config.test_server_id]
    )
    async def switch_pool(
        self, 
        interaction: nextcord.Interaction, 
        value: bool = nextcord.SlashOption(
            name="value",
            description="The boolean value to set",
            required=True
        )
    ):
        """
        Switch the value in awaPool.json.
        
        Args:
            interaction (nextcord.Interaction): The interaction instance
            value (bool): The boolean value to set in the file
        """
        try:
            pool_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "awaPool.json")
            
            with open(pool_path, "r") as f:
                data = json.load(f)
                
            data["normal"] = value
            
            with open(pool_path, "w") as f:
                json.dump(data, f, indent=4)
            
            # Reload all modules to ensure the change takes effect
            success, report = reload_all(self.bot)
            
            if success:
                pool_type = "normal" if value else "buffed"
                await interaction.response.send_message(
                    f"✅ Successfully switched to **{pool_type}** pool!",
                    ephemeral=True
                )
            else:
                msg = ["⚠️ Pool was switched but reload had some issues:"]
                if report["failed"]:
                    msg.extend(f"• {error}" for error in report["failed"])
                await interaction.response.send_message(
                    "\n".join(msg),
                    ephemeral=True
                )
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(SwitchPool(bot))