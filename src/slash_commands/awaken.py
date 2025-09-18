import os, sys
import nextcord
from nextcord.ext import commands

sys.path.append(os.path.abspath("src"))
from utils.functions.awaken import make_response
from utils.config import allowed_channels

class Awaken(commands.Cog):
    """
    Awakening Simulation Command Cog.
    Provides a slash command to simulate hero awakenings with different
    probability pools (normal or buffed) and calculate total resources
    spent and gained.
    """
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Awaken cog.
        
        Args:
            bot (commands.Bot): The bot instance this cog is being added to
        """
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
            allowed_channel = allowed_channels.awaken
            if interaction.guild and isinstance(interaction.channel, nextcord.TextChannel):
                if interaction.channel.name != allowed_channel:
                    await interaction.response.send_message(
                        f"This command can only be used in #{allowed_channel} channel.\n"
                        f"Try if it's there, create one otherwise",
                        ephemeral=True
                    )
                    return
            final_reply = make_response(times) 

            await interaction.response.send_message(final_reply)

        except Exception as e:
            await interaction.response.send_message("Something went wrong, kindly try agian", ephemeral=True)
            print(e)
            

def setup(bot: commands.Bot):
    bot.add_cog(Awaken(bot))
