import nextcord
from nextcord.ext import commands
from agents import Runner
from src.agent.navigator import nav_agent

class ask(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="ask", description="i'm still learning but i'll try my best")
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
