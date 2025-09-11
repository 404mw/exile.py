import nextcord
from nextcord.ext import commands
from src.utils.functions import get_se_hp
from src.utils.config import emojis



class BossHP(commands.Cog):
    """
    Star Expedition (SE) Boss HP Calculator Cog.
    Provides slash commands to calculate boss HP at different levels and percentages.
    """
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the BossHP cog.
        
        Args:
            bot (commands.Bot): The bot instance this cog is being added to
        """
        self.bot = bot

    @nextcord.slash_command(
        name="se",
        description="Easy SE HP"
    )
    async def se_hp(
        self,
        interaction: nextcord.Interaction,
        boss: int = nextcord.SlashOption(
            name="boss",
            description="Enter current boss(1-200)",
            required=True,
            min_value=1,
            max_value=200
        ),
        perc: int = nextcord.SlashOption(
            name="percentage",
            description="Enter remaining percentage(1-100) [optional]",
            required=False,
            min_value=1,
            max_value=100,
            default=100
        )
    ):
        try:
            emoji_hp: str = emojis.hp
            emoji_boss: str = emojis.se2g if boss <= 100 else emojis.se1g
            response: str = "⚠️ Try again"

            print("SE command initialized")

            result: str = get_se_hp(boss, perc)
            print(f"Functions called\n{result}")
            if not result:
                response = f"No available data for {boss}{emoji_boss}"
            else:
                response = f"> **x{boss}** {emoji_hp} at **{perc}%**\n> \n> {emoji_boss} **{result:.13e}** remaining"

            await interaction.response.send_message(response)

        except Exception as e:
            await interaction.response.send_message(
                f"⚠️ Something went wrong and i couldn't get or calculate HP", ephemeral=True
            )
            print(e)

def setup(bot: commands.Bot):
    bot.add_cog(BossHP(bot))
