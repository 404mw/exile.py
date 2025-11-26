from src.utils.config import config


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
    target = getattr(config, 'giveaway_manager_role', 'giveaway manager')
    try:
        return any(getattr(r, 'name', '').lower() == target.lower() for r in getattr(member, 'roles', []))
    except Exception:
        return False
