import nextcord
from nextcord.ext import commands
from src.utils.functions import roll_dice

class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(name="dice", description="Roll a dice")
    async def dice(self, interaction: nextcord.Interaction, sides: int = 6):
        try:
            result = roll_dice(sides)
            await interaction.response.send_message(f"🎲 You rolled {result} (1-{sides})")
        except ValueError as e:
            await interaction.response.send_message(str(e), ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(Dice(bot))
