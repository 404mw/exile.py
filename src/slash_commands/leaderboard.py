import nextcord
from nextcord.ext import commands
from src.utils.config import config, emojis
from src.utils.functions import get_top_users


class Leaderboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="leaderboard",
        description="Show top users by XP",
        guild_ids=[config.exile_server_id]
    )
    async def leaderboard(self, interaction: nextcord.Interaction):
        try:
            await interaction.response.defer()

            top = get_top_users(5)
            if not top:
                await interaction.followup.send("No leaderboard data available.", ephemeral=True)
                return

            embed = nextcord.Embed(
                title=f"{emojis.gopnik} Exile Leaderboard {emojis.gopnik}",
                description="Top 5 users are shown based on thier **Total XP**\n",
                color=0x588543
            )

            # Set bot's avatar as thumbnail
            if self.bot.user and self.bot.user.avatar:
                embed.set_thumbnail(url=self.bot.user.avatar.url)

            # Set thumbnail to leaderboard 1st place avatar
            top_user_id, _ = top[0]
            user = self.bot.get_user(int(top_user_id))
            if user:
                embed.set_thumbnail(url=user.display_avatar.url)

            for idx, (user_id, data) in enumerate(top, start=1):
                level = data.get("level", 1)
                xp = data.get("xp", 0)

                try:
                    user_obj = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(int(user_id))
                    name = user_obj.display_name if user_obj else f"<@{user_id}>"
                except:
                    name = f"<@{user_id}>"

                embed.add_field(
                    name=f"**#{idx} {name}**",
                    value=f"Level `{level}`",
                    inline=True
                )
                embed.add_field(
                    name="\u200b",  # spacer
                    value=f"XP `{xp:,}`",
                    inline=True
                )
                embed.add_field(name="\u200b", value="\u200b")  # line break for spacing

            embed.set_footer(text=f"keep the spam alive {emojis.roo_fire}")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(e)
            if not interaction.response.is_done():
                await interaction.response.send_message("⚠ Something went wrong", ephemeral=True)
            else:
                await interaction.followup.send("⚠ Something went wrong", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Leaderboard(bot))
