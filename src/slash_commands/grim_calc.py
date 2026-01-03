import nextcord
from nextcord.ext import commands
from src.utils.config import emojis
from src.utils.functions.grim_calc import get_grim_calc


class GrimCalc(commands.Cog):
    """
    A cog for the Discord bot that provides a slash command to calculate the
    cost of upgrading Grimoires.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initializes the GrimCalc cog.

        Args:
            bot: The instance of the Discord bot.
        """
        self.bot = bot

    @nextcord.slash_command(
        name="grim_calc",
        description="Calculate Grimoire upgrade costs for either book"
    )
    async def grim_calc(
        self,
        interaction: nextcord.Interaction,
        book: str = nextcord.SlashOption(
            name="book",
            description="Select the Grimoire book",
            required=True,
            choices=["Enable", "Imprint"]
        ),
        goal_lvl: int = nextcord.SlashOption(
            name="goal_lvl",
            description="Target grimoire level (1-150)",
            required=True,
            min_value=1,
            max_value=150
        ),
        current_lvl: int = nextcord.SlashOption(
            name="current_lvl",
            description="Your current grimoire level (1-150)",
            required=False,
            min_value=1,
            max_value=150
        )
    ):
        """
        Calculates the resource cost to upgrade a Grimoire from a current level
        to a target (goal) level.
        """
        try:
            # Defer the response to avoid timeouts
            await interaction.response.defer()

            # Get calculation from the helper function
            result = get_grim_calc(book, goal_lvl, current_lvl)

            # Check for errors returned from the helper
            if result.error:
                await interaction.followup.send(
                    f"⚠️ {result.error}",
                    ephemeral=True
                )
                return

            # Determine book name for the response
            if book.lower() == "enable":
                book_name = f"{emojis.grim_book1} Grimoire • Enabling Chapter"
                level_range = f"`{current_lvl} → {goal_lvl}`" if current_lvl else f"`→ {goal_lvl}`"
                response = (
                    f"> **{book_name}** {level_range}\n"
                    f"> \n"
                    f"> {emojis.grim_essence} `{result.essence_cost:,}` {result.essence_choices:.2f} event choices"
                )
            else:  # Imprint
                book_name = "Grimoire • Imprint Chapter"
                level_range = f"`{current_lvl} → {goal_lvl}`" if current_lvl else f"`→ {goal_lvl}`"
                response = (
                    f"> **{book_name}** {level_range}\n"
                    f"> \n"
                    f"> {emojis.grim_essence} `{result.essence_cost:,}` {result.essence_choices:.2f} event choices\n"
                    f"> {emojis.grim_imprint} `{result.imprint_cost:,}` {result.imprint_choices:.2f} event choices"
                )
            
            await interaction.followup.send(response)

        except Exception as e:
            await interaction.followup.send(
                "⚠️ Something went wrong while calculating grimoire costs.",
                ephemeral=True
            )
            print(f"Error in grim_calc: {e}")


def setup(bot: commands.Bot):
    bot.add_cog(GrimCalc(bot))
