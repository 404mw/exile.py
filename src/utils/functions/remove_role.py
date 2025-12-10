"""Function to remove a role from a user."""
import nextcord
from typing import Union


async def remove_role_from_user(member: nextcord.Member, role: nextcord.Role, actor: Union[nextcord.User, nextcord.Member]) -> tuple[bool, str]:
    """
    Remove a role from a user.
    
    Args:
        member: The member to remove the role from
        role: The role to remove
        actor: The user performing the action (for audit log)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Check if user has the role - refresh member roles first
        if role not in member.roles:
            # Try fetching the member again to ensure we have fresh data
            guild = member.guild
            if guild:
                refreshed_member = guild.get_member(member.id)
                if refreshed_member and role not in refreshed_member.roles:
                    return True, f"✅ {member.mention} does not have the role `{role.name}` to remove."
                member = refreshed_member or member
            else:
                return True, f"✅ {member.mention} does not have the role `{role.name}` to remove."
        
        # Remove the role
        await member.remove_roles(role, reason=f"Removed by {actor}")
        return True, f"✅ Role `{role.name}` removed from {member.mention}"
    
    except nextcord.Forbidden:
        return False, "❌ I don't have permission to remove roles."
    except Exception as e:
        return False, f"❌ An error occurred: {str(e)}"
