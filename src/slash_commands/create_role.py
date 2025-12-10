import nextcord
from nextcord import Interaction, SlashOption, Color, Permissions
from nextcord.ext import commands


class CreateRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="create_role",
        description="Create a new role with default permissions",
        default_member_permissions=Permissions(manage_roles=True)
    )
    async def create_role(
        self,
        interaction: Interaction,
        name: str = SlashOption(description="Name of the role"),
        color: str = SlashOption(description="Color of the role (hex format, e.g., 588543)")
    ):
        """Create a new role in the server with specified name and color."""

        if interaction.user.id != self.bot.owner_id and not interaction.user.guild_permissions.manage_roles:  # type: ignore
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        
        try:
            # Ensure we're in a guild
            if not interaction.guild:
                await interaction.response.send_message(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return

            # Parse color from hex string
            try:
                color_int = int(color.replace("#", ""), 16)
                role_color = Color(color_int)
            except ValueError:
                await interaction.response.send_message(
                    f"Invalid color format. Please use hex format (e.g., 588543 or #588543)",
                    ephemeral=True
                )
                return

            # Create the role with default permissions
            new_role = await interaction.guild.create_role(
                name=name,
                color=role_color,
                reason=f"Created by {interaction.user}"
            )

            await interaction.response.send_message(
                f"✅ Role `{new_role.name}` created successfully with color `#{color.replace('#', '').upper()}`",
                ephemeral=True
            )
        except nextcord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to create roles in this server.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred, Try again",
                ephemeral=True
            )


def setup(bot: commands.Bot):
    bot.add_cog(CreateRole(bot))
