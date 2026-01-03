"""
Centralized configuration for the Discord bot.

This file loads environment variables, defines IDs for emojis, channels, and roles,
and sets up the parameters for the XP and leveling system.

To add or change configuration values, modify the corresponding dataclass instances
at the bottom of this file. For sensitive information like the bot token or specific
role IDs sourced from the environment, create or update the `.env` file in the
project root.
"""
import os
from dotenv import load_dotenv
from .types.config import Emojis, Channels, Config, Roles, XpBonus, XpMultiplier, XpTrueMultiplier, UserIDs

# Load environment variables from the .env file in the project root.
load_dotenv()

# ============================================================================
# CORE CONFIGURATION & ID DEFINITIONS
# ============================================================================

# Load a premium role ID from environment variables.
# This is an example of how to handle sensitive or environment-specific IDs.
PREMIUM_ROLE: int = int(os.environ["PREMIUM_ROLE"])

# Instantiate the dataclasses that hold all the IDs and settings.
emojis = Emojis()
channels = Channels()
roles = Roles(premium_xp=PREMIUM_ROLE)
user_ids = UserIDs()

# Core bot configuration, such as server (guild) IDs.
config = Config(
    test_server_id = 1076157809281994842, # Your test server ID
    exile_server_id = 864172925070082068  # Your main server ID
)

# Optional string name used to identify the role which can manage giveaways.
# Default defined in the Config model; explicit here for clarity.
roles.giveaway_manager_role = getattr(config, 'giveaway_manager_role', 'giveaway manager')


# ============================================================================
# XP BONUSES (STATIC ADDITIONS)
# Tier 1 of the XP calculation. These are flat values added to the base XP.
# ============================================================================

# Add XP bonuses for specific channels.
channels.xp_bonuses = [
    # Example: Grant an extra 17 XP for messages in the 'exile_chat' channel.
    XpBonus(id=channels.exile_chat, amount=17),
]

# Add XP bonuses for specific roles.
roles.xp_bonuses = [
    # Example: Grant an extra 5 XP to users with the 'exile_role'.
    # XpBonus(id=roles.exile_role, amount=5),
]

# ============================================================================
# XP MULTIPLIERS (NORMAL MULTIPLIERS)
# Tier 2 of the XP calculation. These are applied after static additions.
# Multiple multipliers are multiplicative (e.g., 1.5 * 1.2).
# ============================================================================

# Add XP multipliers for specific channels.
channels.xp_multipliers = [
    # Example: Apply a 1.5x multiplier for messages in a specific channel.
    # XpMultiplier(id=866773791560040519, value=1.5)
]

# Add XP multipliers for specific roles.
roles.xp_multipliers = [
    # Example: Apply a 1.5x multiplier to users with the 'exile_role'.
    XpMultiplier(id=roles.exile_role, value=1.5),
]

# ============================================================================
# XP TRUE MULTIPLIERS (FINAL MULTIPLIER)
# Tier 4 of the XP calculation. This is a final, overriding multiplier.
# Only one "true" multiplier is applied per user, even if they have multiple roles.
# ============================================================================

roles.xp_true_multipliers = [
    # Example: Apply a 2x "true" multiplier to server boosters.
    XpTrueMultiplier(id=roles.booster_role, value=2.0),
    # Example: Apply a 2x "true" multiplier to users with the premium role.
    XpTrueMultiplier(id=roles.premium_xp, value=2.0)
]

# ============================================================================
# LEVEL-BASED XP MULTIPLIER
# Tier 3 of the XP calculation. This multiplier scales with the user's level.
# Formula: 1.0 + (user_level * level_multiplier_rate)
# ============================================================================

# The rate at which the level-based multiplier increases per level.
# For example, 0.01 means a 1% XP boost per level.
config.level_multiplier_rate = 0.1