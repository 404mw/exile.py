from src.utils.config import roles


def can_member_start_giveaway(member, is_owner: bool) -> bool:
    """Return True if the member is allowed to start giveaways.

    Allowed when the caller is the bot owner or when the member has a role
    named 'giveaway manager' (case-insensitive).
    """
    if is_owner:
        return True
    if not member:
        return False
    # read the configured target role name and compare case-insensitively
    target = getattr(roles, 'giveaway_manager_role', 'giveaway manager')
    try:
        return any(getattr(r, 'name', '').lower() == target.lower() for r in getattr(member, 'roles', []))
    except Exception:
        return False


def can_member_manage_messages(member, is_owner: bool) -> bool:
    """Return True if the member is allowed to perform moderator message actions.

    Allowed when the caller is the bot owner or when the member has the
    guild permission to manage messages or is an administrator.
    """
    if is_owner:
        return True
    if not member:
        return False

    try:
        perms = getattr(member, 'guild_permissions', None)
        if not perms:
            return False
        # typical moderator-like permissions that imply ability to manage messages
        return bool(
            getattr(perms, 'manage_messages', False)
            or getattr(perms, 'administrator', False)
            or getattr(perms, 'manage_guild', False)
        )
    except Exception:
        return False
