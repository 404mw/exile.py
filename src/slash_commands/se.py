import nextcord
from nextcord.ext import commands
from src.utils.functions import get_se_hp
from src.utils.config import config



class BossHP(commands.Cog):
    def __init__(self, bot: commands.Bot):
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
            emoji_hp: str = config.emojis.hp
            emoji_boss: str = config.emojis.se2g if boss <= 100 else config.emojis.se1g
            response: str = "⚠️ Try again"

            result: str = get_se_hp(boss, perc)
            if result == 0:
                response = f"No available data for {boss}{emoji_boss}"
            else:
                response = f"> **x{boss}** {emoji_hp} at **{perc}%**\n> \n> {emoji_boss} **{result:.13e}** remaining"

            await interaction.response.send_message(response)

        except Exception as e:
            await interaction.response.send_message(
                f"⚠️ Something went wrong and i couldn't get or calculate HP", ephemeral=True
            )

def setup(bot: commands.Bot):
    bot.add_cog(BossHP(bot))
