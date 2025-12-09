from .types.config import Emojis, Channels, Config, Roles

emojis = Emojis()
channels = Channels()
roles = Roles()

config = Config(
    test_server_id = 1076157809281994842,
    exile_server_id = 864172925070082068
)

# Optional string name used to identify the role which can manage giveaways.
# Default defined in the Config model; explicit here for clarity.
roles.giveaway_manager_role = getattr(config, 'giveaway_manager_role', 'giveaway manager')