import nextcord
from nextcord.ext import commands
from src.utils.functions import roll_dice
from src.utils.config import config

class Dice(commands.Cog):
    """
    Dice Rolling Command Cog.
    Provides a slash command to roll a dice with a configurable number of sides.
    """
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Dice cog.
        
        Args:
            bot (commands.Bot): The bot instance this cog is being added to
        """
        self.bot = bot

    @nextcord.slash_command(
            name="dice",
            description="Roll a dice",
            guild_ids=[config.test_server_id]    
        )
    async def dice(self, interaction: nextcord.Interaction, sides: int = 6):
        try:
            result = roll_dice(sides)
            await interaction.response.send_message(f"🎲 You rolled {result} (1-{sides})")
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(Dice(bot))
