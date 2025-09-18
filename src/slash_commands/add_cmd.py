import json
from pathlib import Path
from typing import List, Optional

import nextcord
from nextcord import SlashOption, Interaction
from nextcord.ext import commands

from src.utils.types.msg_commands import MsgCommand
from src.utils.functions.reload_config import reload_all
from src.utils.config import config


def validate_command_name(cmd_name: str, commands_data: List[dict]) -> bool:
    """
    Validate that the command name doesn't conflict with existing aliases.
    
    Args:
        cmd_name: The name to check
        commands_data: The current commands data
        
    Returns:
        bool: True if name is valid (no conflicts), False otherwise
    """
    for cmd in commands_data:
        if cmd.get('aliases') and cmd_name in cmd['aliases']:
            return False
    return True


class AddCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.json_path = Path(__file__).resolve().parents[2] / "data" / "msgCommands.json"

    @nextcord.slash_command(
        name="add_cmd",
        description="Add a new message command or append responses to existing one",
        guild_ids=[config.test_server_id],
        default_member_permissions=8  # Administrator only
    )
    @commands.is_owner()  # Only bot owner can use this command
    async def add_command(
        self,
        interaction: Interaction,
        name: str = SlashOption(
            description = "The name of the command",
            required = True
        ),
        responses: str = SlashOption(
            description = "Command responses (separate multiple with |)",
            required = True
        ),
        aliases: Optional[str] = SlashOption(
            description = "Command aliases (separate multiple with |)",
            required = False
        )
    ):
        try:
            # Load current commands
            with open(self.json_path, "r", encoding="utf-8") as f:
                commands_data = json.load(f)
            
            # Convert responses and aliases to lists
            response_list = [r.strip() for r in responses.split('|')]
            alias_list = [a.strip() for a in aliases.split('|')] if aliases else None
            
            # Validate command name against existing aliases
            if not validate_command_name(name, commands_data):
                await interaction.response.send_message(
                    f"Error: The name '{name}' conflicts with an existing command alias.",
                    ephemeral=True
                )
                return
            
            # Check if command already exists
            existing_cmd = next((cmd for cmd in commands_data if cmd["name"] == name), None)
            
            if existing_cmd:
                # Append new responses to existing command
                existing_cmd["responses"].extend(response_list)
            else:
                # Create new command
                new_cmd = MsgCommand(
                    name=name,
                    responses=response_list,
                    aliases=alias_list
                )
                commands_data.append(new_cmd.model_dump(exclude_none=True))
            
            # Write updated data back to file
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(commands_data, f, indent=2)
            
            # Reload bot configuration
            success, report = reload_all(self.bot)
            action = "updated" if existing_cmd else "added"
            
            if success:
                await interaction.response.send_message(
                    f"Successfully {action} command !`{name}`",
                    ephemeral=True
                )
            else:
                msg = [f"Command !`{name}` was saved but reload had some issues:"]
                if report["failed"]:
                    msg.extend(f"• {error}" for error in report["failed"])
                await interaction.response.send_message(
                    "\n".join(msg),
                    ephemeral=True
                )
                
        except Exception as e:
            await interaction.response.send_message(
                f"Error: {str(e)}",
                ephemeral=True
            )


def setup(bot: commands.Bot):
    bot.add_cog(AddCommand(bot))