import nextcord
from nextcord.ext import commands
from agents import Runner
from src.agent.navigator import nav_agent
from src.utils.config import config

class ask(commands.Cog):
    """
    AI-powered Ask Command Cog.
    Provides a slash command that lets users ask questions which are answered by
    the navigator agent, which routes queries to either game-specific tools or
    the general chat agent.
    """
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the ask cog.
        
        Args:
            bot (commands.Bot): The bot instance this cog is being added to
        """
        self.bot = bot

    @nextcord.slash_command(
            name="ask",
            description="i'm still learning but i'll try my best",
            guild_ids=[config.exile_server_id]
        )
    async def ask(
        self,
        interaction: nextcord.Interaction,
        query: str = nextcord.SlashOption(
            name = "query",
            description = "Ask a general or IH related question",
            required = True
        ),
    ):
        try:
            await interaction.response.defer()
            result = await Runner.run(starting_agent=nav_agent, input=query)
            result = result.final_output

            await interaction.followup.send(result)
        except Exception as e:
            print(e)
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"⚠️ Something went wrong, kindly try again", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"⚠️ Something went wrong, kindly try again", ephemeral=True
                )

def setup(bot: commands.Bot):
    bot.add_cog(ask(bot))
