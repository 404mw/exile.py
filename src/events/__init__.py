"""
Event loader for Discord bot events.
"""
from .on_ready import setup as setup_on_ready
from .on_mention import setup as setup_on_mention

def setup(bot):
    setup_on_ready(bot)
    setup_on_mention(bot)