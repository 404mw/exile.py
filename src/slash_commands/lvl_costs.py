import nextcord
from nextcord import SlashOption
from nextcord.ext import commands
from src.utils.config import config
from src.utils.functions import get_xp_required_for_level


class EachLevelCosts(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="lvl_costs",
        description="Show cumulative XP required to reach a specified level (max 250)",
        guild_ids=[config.exile_server_id]
    )
    async def lvl_costs(
        self,
        interaction: nextcord.Interaction,
        level: int = SlashOption(
            description="Target level (1-250)",
            required=True,
            min_value=1,
            max_value=250
        ),
    ):
        try:
            await interaction.response.defer()

            xp_req = get_xp_required_for_level(level)
            if xp_req is None:
                await interaction.followup.send(
                    f"Could not fetch XP data for level {level}.",
                    ephemeral=True
                )
                return

            await interaction.followup.send(f"Level **{level}** requires **{xp_req:,}** XP", ephemeral=True)

        except Exception as e:
            print(e)
            if not interaction.response.is_done():
                await interaction.response.send_message("⚠️ Something went wrong", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ Something went wrong", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(EachLevelCosts(bot))
