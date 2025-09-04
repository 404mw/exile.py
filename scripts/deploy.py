import os
import sys
import time
import importlib.util
from typing import Dict, Set
import asyncio
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

load_dotenv()
# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import bot configuration
try:
    TOKEN = os.getenv("TOKEN")
    print("Bot token acquired")
except Exception:
    print("Bot token not found")


# Create bot instance
intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}")
    print("Starting command registration...")

class CommandWatcher:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.command_files: Dict[str, float] = {}
        self.registered_commands: Set[str] = set()
        self.commands_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "src",
            "slash_commands"
        )

    def get_file_modification_time(self, filepath: str) -> float:
        """Get the last modification time of a file."""
        return os.path.getmtime(filepath)

    def scan_command_files(self) -> Dict[str, float]:
        """Scan command files and their modification times."""
        command_files = {}
        for filename in os.listdir(self.commands_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                filepath = os.path.join(self.commands_dir, filename)
                command_files[filepath] = self.get_file_modification_time(filepath)
        return command_files

    async def reload_command(self, filepath: str) -> None:
        """Reload a specific command module."""
        try:
            # Get the module name from filepath
            module_name = os.path.splitext(os.path.basename(filepath))[0]
            
            # Remove existing command if it exists
            if module_name in self.registered_commands:
                self.bot.remove_cog(module_name.capitalize())
                self.registered_commands.remove(module_name)
                print(f"Removed command: {module_name}")

            # Unload the module if it exists
            if module_name in sys.modules:
                del sys.modules[module_name]

            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Setup the command
                if hasattr(module, 'setup'):
                    # Call setup function directly
                    module.setup(self.bot)  # setup returns None, don't await it
                    self.registered_commands.add(module_name)
                    print(f"Reloaded command: {module_name}")
                else:
                    print(f"Warning: {module_name} has no setup function")

        except Exception as e:
            print(f"Error reloading {filepath}: {str(e)}")

    async def watch_commands(self):
        """Monitor command files for changes and update them."""
        print("Starting command registration...")
        
        # Initial load of all commands
        current_files = self.scan_command_files()
        command_count = len(current_files)
        registered_count = 0
        
        for filepath, mtime in current_files.items():
            print(f"Loading command: {os.path.basename(filepath)}")
            await self.reload_command(filepath)
            self.command_files[filepath] = mtime
            registered_count += 1
        
        print(f"\nRegistered {registered_count}/{command_count} commands successfully")

async def main():
    if not TOKEN:
        print("Error: No bot token found in environment variables")
        return

    try:
        print("Starting bot...")
        # First, login without starting the websocket
        await bot.login(TOKEN)
        
        print("Starting command registration...")
        watcher = CommandWatcher(bot)
        await watcher.watch_commands()
        
        print("\nCommand registration complete. Cleaning up...")
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        try:
            await bot.http.close()
            await bot.close()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
        print("Bot shutdown completed successfully.")
    except KeyboardInterrupt:
        print("\nBot shutdown completed.")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)
