import nextcord
from nextcord import Interaction, SlashOption, Permissions
from nextcord.ext import commands
from src.utils.config import config
from src.utils.functions.add_role import add_role_to_user
from src.utils.functions.remove_role import remove_role_from_user


class ManageRole(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="manage_role",
        description="Manage roles by adding or removing them from users",
    )
    async def manage_role(
        self,
        interaction: Interaction,
        action: str = SlashOption(
            description="Choose an action",
            choices=["add role", "remove role"]
        ),
        user: nextcord.User = SlashOption(description="Select a user"),
        role: nextcord.Role = SlashOption(description="Select a role")
    ):
        """Manage roles for server users - add or remove roles."""

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

            # Get the member object from the user - fetch fresh data
            member = await interaction.guild.fetch_member(user.id)
            if not member:
                await interaction.response.send_message(
                    f"❌ User {user} is not a member of this server.",
                    ephemeral=True
                )
                return

            if action == "add role":
                actor = interaction.user if interaction.user else interaction.client.user
                _, message = await add_role_to_user(member, role, actor)
                await interaction.response.send_message(message, ephemeral=True)

            elif action == "remove role":
                actor = interaction.user if interaction.user else interaction.client.user
                _, message = await remove_role_from_user(member, role, actor)
                await interaction.response.send_message(message, ephemeral=True)

        except nextcord.NotFound:
            await interaction.response.send_message(
                f"❌ User not found in this server.",
                ephemeral=True
            )
        except nextcord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage roles in this server.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )


def setup(bot: commands.Bot):
    bot.add_cog(ManageRole(bot))
