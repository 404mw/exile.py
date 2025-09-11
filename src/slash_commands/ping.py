import nextcord
from nextcord.ext import commands
from src.utils.functions import get_ping_response
from src.utils.config import config

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
            name = "ping",
            description = "Check latency",
            guild_ids = [config.test_server_id]
        )
    async def ping(self, interaction: nextcord.Interaction):
        response = get_ping_response(self.bot.latency)
        await interaction.response.send_message(response)

def setup(bot: commands.Bot):
    bot.add_cog(Ping(bot))
