import json
from pathlib import Path
from typing import Optional

import nextcord
from nextcord import SlashOption, Interaction
from nextcord.ext import commands

from src.utils.functions.reload_config import reload_all
from src.utils.config import config


def validate_command_name(cmd_name: str, lookup: dict) -> bool:
    """
    Validate that the command name doesn't conflict with existing aliases.
    
    Args:
        cmd_name: The name to check
        lookup: The lookup table from commands data
        
    Returns:
        bool: True if name is valid (no conflicts), False otherwise
    """
    return cmd_name.lower() not in lookup


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
                data = json.load(f)
            
            commands_dict = data.get("commands", {})
            lookup = data.get("lookup", {})
            
            # Convert responses and aliases to lists
            response_list = [r.strip() for r in responses.split('|')]
            alias_list = [a.strip() for a in aliases.split('|')] if aliases else []
            
            # Normalize command name
            normalized_name = name.lower()
            
            # Validate command name against existing commands/aliases
            if not validate_command_name(normalized_name, lookup):
                await interaction.response.send_message(
                    f"Error: The name '{name}' conflicts with an existing command.",
                    ephemeral=True
                )
                return
            
            # Check if command already exists
            existing_cmd = commands_dict.get(normalized_name)
            
            if existing_cmd:
                # Append new responses to existing command
                existing_cmd["responses"].extend(response_list)
                action = "updated"
            else:
                # Create new command
                commands_dict[normalized_name] = {
                    "aliases": alias_list,
                    "responses": response_list
                }
                
                # Add command name to lookup
                lookup[normalized_name] = normalized_name
                
                # Add each alias to lookup
                for alias in alias_list:
                    lookup[alias.lower()] = normalized_name
                
                action = "added"
            
            # Update lookup for existing command if new aliases were added
            if existing_cmd and alias_list:
                # Add any new aliases to lookup
                for alias in alias_list:
                    lookup[alias.lower()] = normalized_name
                # Update the aliases in the command
                existing_cmd["aliases"].extend(alias_list)
            
            # Write updated data back to file
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            # Reload bot configuration
            success, report = reload_all(self.bot)
            
            if success:
                await interaction.response.send_message(
                    f"Successfully {action} command `{name}`",
                    ephemeral=True
                )
            else:
                msg = [f"Command `{name}` was saved but reload had some issues:"]
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