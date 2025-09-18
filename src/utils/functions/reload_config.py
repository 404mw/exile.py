# Made with Claude Sonnet 3.5

from typing import Dict, List, Tuple, cast
import importlib
import os
from nextcord.ext import commands
from src.message_commands.msg_commands import MessageCommands
import sys


def reload_all(bot: commands.Bot) -> Tuple[bool, Dict[str, List[str]]]:
    """
    Reload all bot modules, cogs, and configurations.
    
    Args:
        bot (commands.Bot): The bot instance to reload
        
    Returns:
        Tuple[bool, Dict[str, List[str]]]: A tuple containing:
            - bool: True if the overall reload was successful
            - Dict: Report of successful and failed reloads
    """
    report = {
        "success": [],
        "failed": []
    }
    
    try:
        # Reload all cogs and modules
        cog_dir = "src"
        for root, dirs, files in os.walk(cog_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    try:
                        file_path = os.path.join(root, file)
                        module_path = os.path.splitext(file_path)[0].replace(os.path.sep, ".")
                        
                        # Reload the module if it's loaded
                        if module_path in sys.modules:
                            importlib.reload(sys.modules[module_path])
                            report["success"].append(f"Module: {module_path}")
                            
                            # If it's a cog, reload it in the bot
                            cog_name = file[:-3]
                            try:
                                if bot.get_cog(cog_name):
                                    bot.reload_extension(module_path)
                                    report["success"].append(f"Cog: {cog_name}")
                            except Exception as e:
                                report["failed"].append(f"Cog {cog_name}: {str(e)}")
                    except Exception as e:
                        report["failed"].append(f"Module {file}: {str(e)}")
        
        # Try to reload message commands if the cog exists
        msg_commands_cog = bot.get_cog('MessageCommands')
        if msg_commands_cog:
            try:
                typed_cog = cast(MessageCommands, msg_commands_cog)
                typed_cog.commands_data = typed_cog.load_commands()
                report["success"].append("Message Commands Config")
            except Exception as e:
                report["failed"].append(f"Message Commands Config: {str(e)}")
                
        return len(report["failed"]) == 0, report
        
    except Exception as e:
        report["failed"].append(f"Critical error: {str(e)}")
        return False, report