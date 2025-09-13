from typing import cast
from nextcord.ext import commands
from src.message_commands.msg_commands import MessageCommands


def reload_msg_commands(bot: commands.Bot) -> bool:
    """
    Reload message commands configuration without restarting the bot.
    
    Args:
        bot (commands.Bot): The bot instance to update
        
    Returns:
        bool: True if reload was successful, False otherwise
    """
    try:
        # Get the MessageCommands cog and cast it to the correct type
        cog = cast(MessageCommands, bot.get_cog('MessageCommands'))
        if not cog:
            print("[ERROR] MessageCommands cog not found")
            return False
            
        try:
            # Reload commands data
            cog.commands_data = cog.load_commands()
            return True
        except AttributeError:
            print("[ERROR] Failed to access cog attributes")
            return False
        
    except Exception as e:
        print(f"[ERROR] Failed to reload message commands: {e}")
        return False