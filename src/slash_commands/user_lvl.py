import nextcord
from nextcord import SlashOption
from nextcord.ext import commands
from src.utils.config import config
from src.utils.functions import fetch_user_level


class UserLvl(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="user_lvl",
        description="Show a user's level and XP",
        guild_ids=[config.exile_server_id]
    )
    async def user_lvl(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.User = SlashOption(description="User to look up, defaults to yourself", required=False),
    ):
        target = user or interaction.user

        try:
            await interaction.response.defer()

            info = fetch_user_level(target.id)
            if not info:
                await interaction.followup.send(f"No level data found for {target.mention}", ephemeral=True)
                return

            # Compute progress and remaining
            xp_progress = info.get("xp_progress") if info.get("xp_progress") is not None else info.get("xp", 0)
            xp_for_next = info.get("xp_for_next_level") if info.get("xp_for_next_level") is not None else 0
            xp_remaining = max(0, xp_for_next - xp_progress) if xp_for_next else 0

            embed = nextcord.Embed(
                title=f"{target.display_name}'s Level",
                color=0x588543
            )

            # thumbnail as user's avatar
            try:
                embed.set_thumbnail(url=target.display_avatar.url)
            except Exception:
                pass

            embed.add_field(name="Level", value=str(info.get("level", "N/A")), inline=True)
            embed.add_field(name="Total XP", value=str(info.get("xp", 0)), inline=True)
            embed.add_field(
                name="Progress",
                value=f"{xp_progress} / {xp_for_next} (remaining XP till the next level: {xp_remaining})",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(e)
            if not interaction.response.is_done():
                await interaction.response.send_message("⚠️ Something went wrong", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ Something went wrong", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(UserLvl(bot))
