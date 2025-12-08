import json
import nextcord
from nextcord.ext import commands
from src.utils.config import emojis


class GrimCalc(commands.Cog):
    """
    Grimoire Calculator Cog.
    Provides slash commands to calculate grimoire upgrade costs.
    """
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the GrimCalc cog.
        
        Args:
            bot (commands.Bot): The bot instance this cog is being added to
        """
        self.bot = bot
        self.grim1_cost = self._load_json_data("data/grim1Cost.json")
        self.grim2_cost = self._load_json_data("data/grim2Cost.json")

    def _load_json_data(self, file_path: str) -> dict:
        """
        Load JSON data from file.
        
        Args:
            file_path (str): Path to the JSON file
            
        Returns:
            dict: Loaded JSON data
        """
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {file_path} not found")
            return {}

    def _calculate_event_choices(self, essence: int = 0, imprint: int = 0) -> tuple:
        """
        Calculate number of event choices needed for given resources.
        Each event choice gives 1400k essence or 175k imprint.
        
        Args:
            essence (int): Amount of essence needed
            imprint (int): Amount of imprint needed
            
        Returns:
            tuple: (essence_choices, imprint_choices) as float values
        """
        essence_choices = essence / 1400000 if essence > 0 else 0
        imprint_choices = imprint / 175000 if imprint > 0 else 0
        return essence_choices, imprint_choices

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
            description="your current grimoire level (1-150)",
            required=False,
            min_value=1,
            max_value=150
        )
    ):
        try:
            # Validate goal_lvl > current_lvl if current_lvl is provided
            if current_lvl is not None and goal_lvl <= current_lvl:
                await interaction.response.send_message(
                    f"{emojis.point_laugh} You need a higher goal than your current level. It’s cute watching you try, like a goldfish attempting calculus.{emojis.laugh}",
                    ephemeral=True
                )
                return

            # Select the appropriate cost data based on book type
            if book.lower() == "enable":
                cost_data = self.grim1_cost
                book_name = f"{emojis.grim_book1} Grimoire • Enabling Chapter"
            else:  # Imprint
                cost_data = self.grim2_cost
                book_name = "Grimoire • Imprint Chapter"

            # If no current level provided, respond with just the goal level cost
            if current_lvl is None:
                goal_cost = cost_data.get(str(goal_lvl))
                
                if goal_cost is None:
                    await interaction.response.send_message(
                        f"⚠️ No data available for level {goal_lvl}",
                        ephemeral=True
                    )
                    return

                # For grim1Cost (essence), cost_data[lvl] is just an int
                if isinstance(goal_cost, int):
                    essence_choices, _ = self._calculate_event_choices(essence=goal_cost)
                    response = f"> **{book_name}** → `{goal_lvl}`\n> \n> {emojis.grim_essence} `{goal_cost:,}` {essence_choices:.2f} event choices"
                # For grim2Cost (imprint), cost_data[lvl] is a dict with essence and imprint keys
                else:
                    essence_cost = goal_cost.get("essence", 0)
                    imprint_cost = goal_cost.get("imprint", 0)
                    essence_choices, imprint_choices = self._calculate_event_choices(essence=essence_cost, imprint=imprint_cost)
                    response = f"> **{book_name}** → `{goal_lvl}`\n> \n> {emojis.grim_essence} `{essence_cost:,}` {essence_choices:.2f} event choices\n> {emojis.grim_imprint} `{imprint_cost:,}` {imprint_choices:.2f} event choices"

                await interaction.response.send_message(response)
                return

            # Calculate difference between current and goal level
            current_cost = cost_data.get(str(current_lvl))
            goal_cost = cost_data.get(str(goal_lvl))

            if current_cost is None or goal_cost is None:
                await interaction.response.send_message(
                    f"⚠️ No data available for the specified levels",
                    ephemeral=True
                )
                return

            # Calculate the difference
            # For grim1Cost (essence), values are ints
            if isinstance(current_cost, int):
                cost_difference = goal_cost - current_cost
                essence_choices, _ = self._calculate_event_choices(essence=cost_difference)
                response = f"> **{book_name}** `{current_lvl} → {goal_lvl}`\n> \n> {emojis.grim_essence} `{cost_difference:,}` {essence_choices:.2f} event choices"
            # For grim2Cost (imprint), values are dicts
            else:
                essence_current = current_cost.get("essence", 0)
                essence_goal = goal_cost.get("essence", 0)
                imprint_current = current_cost.get("imprint", 0)
                imprint_goal = goal_cost.get("imprint", 0)

                essence_diff = essence_goal - essence_current
                imprint_diff = imprint_goal - imprint_current

                essence_choices, imprint_choices = self._calculate_event_choices(essence=essence_diff, imprint=imprint_diff)
                response = f"> **{book_name}** `{current_lvl} → {goal_lvl}`\n> \n> {emojis.grim_essence} `{essence_diff:,}` {essence_choices:.2f} event choices\n> {emojis.grim_imprint} `{imprint_diff:,}` {imprint_choices:.2f} event choices"

            await interaction.response.send_message(response)

        except Exception as e:
            await interaction.response.send_message(
                f"⚠️ Something went wrong while calculating grimoire costs",
                ephemeral=True
            )
            print(f"Error in grim_calc: {e}")


def setup(bot: commands.Bot):
    bot.add_cog(GrimCalc(bot))
