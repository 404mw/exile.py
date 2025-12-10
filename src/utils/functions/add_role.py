"""Function to add a role to a user."""
import nextcord
from typing import Union


async def add_role_to_user(member: nextcord.Member, role: nextcord.Role, actor: Union[nextcord.User, nextcord.Member]) -> tuple[bool, str]:
    """
    Add a role to a user.
    
    Args:
        member: The member to add the role to
        role: The role to add
        actor: The user performing the action (for audit log)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Check if user already has the role
        if role in member.roles:
            return False, f"⚠️ {member.mention} already has the role `{role.name}`."
        
        # Add the role
        await member.add_roles(role, reason=f"Added by {actor}")
        return True, f"✅ Role `{role.name}` added to {member.mention}"
    
    except nextcord.Forbidden:
        return False, "❌ I don't have permission to add roles."
    except Exception as e:
        return False, f"❌ An error occurred: {str(e)}"
