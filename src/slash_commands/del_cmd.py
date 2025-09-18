import json
from pathlib import Path
import nextcord
from nextcord import SlashOption, Interaction
from nextcord.ext import commands
from src.utils.config import config
from src.utils.functions.reload_config import reload_all


class DeleteCommand(commands.Cog):
    """
    Delete Command Cog.
    Provides a slash command to remove existing message commands.
    """
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the DeleteCommand cog.
        
        Args:
            bot (commands.Bot): The bot instance this cog is being added to
        """
        self.bot = bot
        self.json_path = Path(__file__).resolve().parents[2] / "data" / "msgCommands.json"

    def load_commands(self):
        """Load current commands from JSON file."""
        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_commands(self, commands_data):
        """Save updated commands back to JSON file."""
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(commands_data, f, indent=2)

    @nextcord.slash_command(
        name="del_cmd",
        description="Delete an existing message command",
        guild_ids=[config.test_server_id]
    )
    @commands.is_owner()  # Only bot owner can use this command
    async def delete_command(
        self,
        interaction: Interaction,
        name: str = SlashOption(
            description="The name of the command to delete",
            required=True
        )
    ):
        """Delete a message command from the configuration."""
        try:
            await interaction.response.defer(ephemeral=True)
            
            # Load current commands
            commands_data = self.load_commands()
            
            # Find command by name
            command_index = next(
                (index for index, cmd in enumerate(commands_data) 
                 if cmd["name"].lower() == name.lower()),
                None
            )
            
            if command_index is None:
                await interaction.followup.send(
                    f"❌ Command `{name}` not found.",
                    ephemeral=True
                )
                return
                
            # Remove the command
            removed_command = commands_data.pop(command_index)
            
            # Save updated commands
            self.save_commands(commands_data)
            
            # Reload bot configuration
            success, report = reload_all(self.bot)
            
            # Create response message including aliases if they exist
            aliases_info = ""
            if "aliases" in removed_command and removed_command["aliases"]:
                aliases = ", ".join(f"`{alias}`" for alias in removed_command["aliases"])
                aliases_info = f"\nAliases removed: {aliases}"
            
            if success:
                await interaction.followup.send(
                    f"✅ Successfully deleted command `{name}`!{aliases_info}",
                    ephemeral=True
                )
            else:
                msg = [f"⚠️ Command `{name}` was deleted but reload had some issues:"]
                if report["failed"]:
                    msg.extend(f"• {error}" for error in report["failed"])
                await interaction.followup.send(
                    "\n".join(msg),
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )


def setup(bot: commands.Bot):
    bot.add_cog(DeleteCommand(bot))