import json
import random
import re
from pathlib import Path

import nextcord
from nextcord.ext import commands

from src.utils.config import config


class MessageCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.prefix = config.PREFIX
        self.commands_data = self.load_commands()

    def load_commands(self):
        """Load the commands.json file from the same directory."""
        json_path = Path(__file__).parent / "msgCommands.json"
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def normalize(self, text: str) -> str:
        """Lowercase and strip punctuation for matching."""
        return re.sub(r"[^a-z0-9\s]", "", text.lower()).strip()

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        # ignore bots (including itself)
        if message.author.bot:
            return

        content = message.content
        if not content.startswith(self.prefix):
            return
        
        # strip prefix and normalize input
        command_text = self.normalize(content[len(self.prefix):])

        for cmd in self.commands_data:
            name = self.normalize(cmd["name"])
            aliases = [self.normalize(alias) for alias in cmd.get("aliases", [])]

            if command_text.startswith(name) or any(command_text.startswith(a) for a in aliases):
                responses = cmd.get("responses", [])
                if responses:
                    response = random.choice(responses)

                    # Check if response is media 
                    if response.startswith("./media"):
                        # Go up two levels from this file (src/messagecommand) → root/
                        project_root = Path(__file__).resolve().parents[2]
                        file_path = project_root / response[2:]  # strip "./" from response
                        
                        if file_path.exists():
                            await message.reply(file=nextcord.File(file_path))
                        else:
                            print(f"[WARN] Media file not found: {file_path}")
                    else:
                        await message.reply(response)


                return  # stop after first match


def setup(bot: commands.Bot):
    bot.add_cog(MessageCommands(bot))
