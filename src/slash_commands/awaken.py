import os, sys
import nextcord
from nextcord.ext import commands

sys.path.append(os.path.abspath("src"))
from utils.functions.awaken import run_multiple_selections, make_response
from utils.config import config

class Awaken(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="awaken",
        description="Awakenings Simulation"
    )
    async def awaken(
        self,
        interaction: nextcord.Interaction,
        times: int = nextcord.SlashOption(
            name = "times",
            description = "Number of times to awaken",
            required = True,
            min_value = 1,
            max_value = 999,
            default = 1
        )
    ):
        try:
            # Check whether its an allowed channel or not
            # allowed_channel = config.allowed_channels.awaken
            allowed_channel = "spam"
            if interaction.guild and isinstance(interaction.channel, nextcord.TextChannel):
                if interaction.channel.name != allowed_channel:
                    await interaction.response.send_message(
                        f"This command can only be used in #{allowed_channel} channel.\n"
                        f"Try if it exists, create one otherwise",
                        ephemeral=True
                    )
                    return
            func_result = run_multiple_selections(times)
            final_reply = make_response(times, func_result) 

            await interaction.response.send_message(final_reply)

        except Exception as e:
            await interaction.response.send_message("Something went wrong, kindly try agian", ephemeral=True)
            print(e)
            

def setup(bot: commands.Bot):
    bot.add_cog(Awaken(bot))
