import nextcord
from nextcord.ext import commands
from src.utils.config import config, emojis
from src.utils.functions import get_top_users


class Leaderboard(commands.Cog):
    """
    Encapsulates the `/leaderboard` command, which displays the top users by XP.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="leaderboard",
        description="Show top users by XP",
        guild_ids=[config.exile_server_id]
    )
    async def leaderboard(self, interaction: nextcord.Interaction):
        """
        Displays a leaderboard of the top users in the server based on total XP.

        This command fetches the top 5 users, formats their level and XP into a
        visually appealing embed, and displays it to the channel.

        Args:
            interaction: The `nextcord.Interaction` object representing the command invocation.
        """
        try:
            # Defer the response to allow time for data fetching and processing.
            await interaction.response.defer()

            # Fetch the top 5 users from the user level data.
            top = get_top_users(5)
            if not top:
                await interaction.followup.send("No leaderboard data available.", ephemeral=True)
                return

            # ============================================================================
            # EMBED CREATION
            # ============================================================================

            embed = nextcord.Embed(
                title=f"{emojis.gopnik} Exile Leaderboard {emojis.gopnik}",
                description="Top 5 users are shown based on thier **Total XP**\n",
                color=0x588543
            )

            # Attempt to set the thumbnail to the avatar of the #1 ranked user.
            try:
                top_user_id, _ = top[0]
                user = await self.bot.fetch_user(int(top_user_id))
                if user and user.display_avatar:
                    embed.set_thumbnail(url=user.display_avatar.url)
            except (nextcord.NotFound, IndexError):
                # Fallback to the bot's avatar if the top user can't be fetched.
                if self.bot.user and self.bot.user.avatar:
                    embed.set_thumbnail(url=self.bot.user.avatar.url)

            # ============================================================================
            # POPULATE EMBED WITH TOP USERS
            # ============================================================================
            
            # Iterate through the top users and add them as fields to the embed.
            for idx, (user_id, data) in enumerate(top, start=1):
                level = data.get("level", 1)
                xp = data.get("xp", 0)

                # Fetch the user object to get their display name.
                try:
                    user_obj = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(int(user_id))
                    name = user_obj.display_name if user_obj else f"<@{user_id}>"
                except nextcord.NotFound:
                    # If the user can't be fetched, fall back to mentioning their ID.
                    name = f"Unknown User (ID: {user_id})"

                # Add a field for each user, including rank, name, level, and XP.
                embed.add_field(
                    name=f"**#{idx} {name}**",
                    value=f"Level `{level}`",
                    inline=True
                )
                embed.add_field(
                    name="\u200b",  # Use a zero-width space for alignment.
                    value=f"XP `{xp:,}`",
                    inline=True
                )
                embed.add_field(name="\u200b", value="\u200b", inline=False) # Use a field as a line break for spacing.

            embed.set_footer(text=f"keep the spam alive {emojis.roo_fire}")

            # Send the completed leaderboard embed.
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"Error in /leaderboard command: {e}")
            # Gracefully handle any unexpected errors.
            if not interaction.response.is_done():
                await interaction.response.send_message("⚠ Something went wrong", ephemeral=True)
            else:
                await interaction.followup.send("⚠ Something went wrong", ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Leaderboard(bot))
