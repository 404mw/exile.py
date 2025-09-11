import sys
import os

sys.path.append(os.path.abspath("src"))
import nextcord
from nextcord.ext import commands
from pydantic import BaseModel, Field
from utils.functions import get_dt_calc
from utils.temple_cost import temple_cost as temp_cost
from utils.config import emojis


class TempleRequirement(BaseModel):
    """Pydantic model for temple level requirements"""
    gem: int
    spiritvein: int


class CalculationResult(BaseModel):
    """Pydantic model for calculation results"""
    user_gems: int = Field(default=0)
    user_spirits: int = Field(default=0)
    required_gems: int = Field(default=0)
    required_spiritveins: int = Field(default=0)


class ResourceInfo(BaseModel):
    """Pydantic model to store resource information for better organization"""
    gems: int
    spirits: int
    emoji_gem: str
    emoji_spirit: str

    def format_amount(self, amount: int, resource_type: str) -> str:
        """Format resource amount with proper emoji"""
        emoji = self.emoji_gem if resource_type == "gem" else self.emoji_spirit
        return f"`{abs(amount)}`{emoji}"

    @classmethod
    def from_calc_result(cls, calc_result, config):
        """Create ResourceInfo from calculation result"""
        return cls(
            gems=calc_result.user_gems,
            spirits=calc_result.user_spirits,
            emoji_gem=config.emojis.gem,
            emoji_spirit=config.emojis.spiritvein
        )


class DTCalc(commands.Cog):
    """Divine Temple Calculator Cog for handling temple resource calculations"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _format_temple_requirements(self, level: int, temple_req: TempleRequirement, resources: ResourceInfo) -> str:
        """Format the temple requirements message"""
        return f"""**Temple {level} Requires** -> {resources.format_amount(temple_req.gem, 'gem')} {resources.format_amount(temple_req.spiritvein, 'spirit')}"""

    def _format_user_resources(self, resources: ResourceInfo) -> str:
        """Format the user's current resources message"""
        return f"""\n**What you have** -> {resources.format_amount(resources.gems, 'gem')} {resources.format_amount(resources.spirits, 'spirit')}\n"""
        

    def _format_resource_difference(self, result: CalculationResult, resources: ResourceInfo) -> str:
        """Format the resource difference message (excess or missing)"""
        response = ""
        
        # Check for excess resources
        if result.required_gems < 0 or result.required_spiritveins < 0:
            response += "\n**You Exceed** -> "
            if result.required_gems < 0:
                response += f"{resources.format_amount(-result.required_gems, 'gem')} "
            if result.required_spiritveins < 0:
                response += f"{resources.format_amount(-result.required_spiritveins, 'spirit')}"
        
        # Check for missing resources
        if result.required_gems > 0 or result.required_spiritveins > 0:
            response += "\n**You are Missing** -> "
            if result.required_gems > 0:
                response += f"{resources.format_amount(result.required_gems, 'gem')} "
            if result.required_spiritveins > 0:
                response += f"{resources.format_amount(result.required_spiritveins, 'spirit')}"
        
        return response

    @nextcord.slash_command(
        name="dt_calc",
        description="Calculate Divine Temple resource requirements and compare with your current resources",
        force_global=True  # Forces global command registration
    )
    async def dt_calc(
        self,
        interaction: nextcord.Interaction,
        temple_level: int = nextcord.SlashOption(
            name="temple_level",
            description="Enter your goal temple level here to compare (limit 1-22)",
            min_value=1,
            max_value=22,
            required=True
        ),
        origin: int = nextcord.SlashOption(
            name="origin",
            description="Enter Origin(D1) heroes here (limit 0-16)",
            min_value=0,
            max_value=16,
            required=False,
            default=0
        ),
        surge: int = nextcord.SlashOption(
            name="surge",
            description="Enter Surge(D2) heroes here (limit 0-16)",
            min_value=0,
            max_value=16,
            required=False,
            default=0
        ),
        chaos: int = nextcord.SlashOption(
            name="chaos",
            description="Enter Chaos(D3) heroes here (limit 0-16)",
            min_value=0,
            max_value=16,
            required=False,
            default=0
        ),
        core: int = nextcord.SlashOption(
            name="core",
            description="Enter Core(D4) heroes here (limit 0-16)",
            min_value=0,
            max_value=16,
            required=False,
            default=0
        ),
        polystar: int = nextcord.SlashOption(
            name="polystar",
            description="Enter Polystar(D5) heroes here (limit 0-16)",
            min_value=0,
            max_value=16,
            required=False,
            default=0
        ),
        nirvana: int = nextcord.SlashOption(
            name="nirvana",
            description="Enter Nirvana(D6) heroes here (limit 0-12)",
            min_value=0,
            max_value=12,
            required=False,
            default=0
        ),
        bag_aurora: int = nextcord.SlashOption(
            name="bag_aurora",
            description="Enter Aurora Gems from bag here (limit 0-100)",
            min_value=0,
            max_value=100,
            required=False,
            default=0
        ),
        bag_spirit: int = nextcord.SlashOption(
            name="bag_spirit",
            description="Enter Scattered Spiritvein Shards from bag here (max 999999)",
            min_value=0,
            max_value=999999,
            required=False,
            default=0
        ),
    ):
        """
        Calculate Divine Temple resource requirements and compare with current resources.
        This command helps players plan their temple upgrades by showing required and missing resources.
        """
        try:
            # Calculate user's resources and requirements
            calc_result = CalculationResult(**get_dt_calc(
                goal_temple=temple_level,
                origin=origin,
                surge=surge,
                chaos=chaos,
                core=core,
                polystar=polystar,
                nirvana=nirvana,
                bag_gems=bag_aurora,
                bag_spirit=bag_spirit,
            ).__dict__)
            
            temple_req = TempleRequirement(
                gem=temp_cost[temple_level - 1].gem,
                spiritvein=temp_cost[temple_level - 1].spiritvein
            )

            # Create ResourceInfo instance for consistent formatting
            resources = ResourceInfo(
                gems=calc_result.user_gems or 0,
                spirits=calc_result.user_spirits or 0,
                emoji_gem=emojis.gem,
                emoji_spirit=emojis.spiritvein
            )

            # Build response message
            response = self._format_temple_requirements(temple_level, temple_req, resources)
            
            if resources.gems > 0:  # Only show user resources if they have any
                response += self._format_user_resources(resources)
                response += self._format_resource_difference(calc_result, resources)

            await interaction.response.send_message(response)
            
        except Exception:
            await interaction.response.send_message(
                "An error occurred while calculating temple resources. Please try again.",
                ephemeral=True
            )

def setup(bot: commands.Bot):
    bot.add_cog(DTCalc(bot))