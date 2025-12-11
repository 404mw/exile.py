import os
from dotenv import load_dotenv
from .types.config import Emojis, Channels, Config, Roles, XpBonus, XpMultiplier, XpTrueMultiplier, UserIDs

load_dotenv()
PREMIUM_ROLE: int = int(os.environ["PREMIUM_ROLE"])

emojis = Emojis()
channels = Channels()
roles = Roles(premium_xp=PREMIUM_ROLE)
user_ids = UserIDs()

config = Config(
    test_server_id = 1076157809281994842,
    exile_server_id = 864172925070082068
)

# Optional string name used to identify the role which can manage giveaways.
# Default defined in the Config model; explicit here for clarity.
roles.giveaway_manager_role = getattr(config, 'giveaway_manager_role', 'giveaway manager')



# ============================================================================
# XP BONUSES (Static Additions)
# ============================================================================
# Add XP bonuses for specific channels and roles

channels.xp_bonuses = [
    XpBonus(id=channels.exile_chat, amount=17),
    
]

roles.xp_bonuses = [
    # XpBonus(id=roles.exile_role, amount=5),
    
]

# ============================================================================
# XP MULTIPLIERS (Normal Multipliers)
# ============================================================================
# Add XP multipliers for specific roles (and channels)

# Channel-based multipliers
channels.xp_multipliers = [
    # XpMultiplier(id=866773791560040519, value=1.5)
    
]

# Role-based multipliers
roles.xp_multipliers = [
    XpMultiplier(id=roles.exile_role, value=1.5),
    
]

# ============================================================================
# XP TRUE MULTIPLIERS (Applied Last)
# ============================================================================
# Add true multipliers for specific roles

roles.xp_true_multipliers = [
    XpTrueMultiplier(id=roles.booster_role, value=2.0),
    XpTrueMultiplier(id=roles.premium_xp, value=2.0)
]

# ============================================================================
# LEVEL-BASED XP MULTIPLIER
# ============================================================================
# Multiplier increases by level_multiplier_rate for each user level
config.level_multiplier_rate = 0.1