from .types.config import Emojis, Channels, Config

emojis = Emojis()
channels = Channels()

config = Config(
    test_server_id = 1076157809281994842,
    exile_server_id = 864172925070082068
)

# Optional string name used to identify the role which can manage giveaways.
# Default defined in the Config model; explicit here for clarity.
config.giveaway_manager_role = getattr(config, 'giveaway_manager_role', 'giveaway manager')