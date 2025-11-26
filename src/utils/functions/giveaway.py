import json
import os
from datetime import datetime
from typing import List, Optional
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import nextcord
from typing import Iterable
from src.utils.types.giveaway import Giveaway

GIVEAWAY_JSON = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', 'data', 'giveaway.json')
scheduler = AsyncIOScheduler()

# --- JSON Management ---
def load_giveaways() -> List[Giveaway]:
    if not os.path.exists(GIVEAWAY_JSON):
        return []
    with open(GIVEAWAY_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return [Giveaway(**g) for g in data]

def save_giveaways(giveaways: List[Giveaway]):
    with open(GIVEAWAY_JSON, 'w', encoding='utf-8') as f:
        json.dump([g.dict() for g in giveaways], f, default=str, indent=2)

# --- Expired Giveaways ---
def delete_expired_giveaways():
    giveaways = load_giveaways()
    now = datetime.utcnow()
    active = [g for g in giveaways if g.end_time > now and g.active]
    save_giveaways(active)
    # Remove jobs from scheduler
    for job in scheduler.get_jobs():
        if not any(g.id == job.id for g in active):
            scheduler.remove_job(job.id)

# --- Active Giveaway ---
def get_active_giveaway() -> Optional[Giveaway]:
    giveaways = load_giveaways()
    now = datetime.utcnow()
    for g in giveaways:
        if g.active and g.end_time > now:
            return g
    return None

# --- Start Giveaway ---
def start_giveaway(giveaway: Giveaway):
    giveaways = load_giveaways()
    giveaways.append(giveaway)
    save_giveaways(giveaways)
    # We keep persistence and a lightweight scheduler for cleanup. The
    # actual announcement/editing of messages should be handled by the
    # bot cog (it has access to the API). The scheduler keeps a job so the
    # store can be updated if the bot isn't running at the exact end time.
    try:
        scheduler.add_job(end_giveaway, 'date', run_date=giveaway.end_time, args=[giveaway.id], id=giveaway.id)
    except Exception:
        # If a job with that id already exists or scheduler isn't running,
        # we ignore — caller (the cog) will also handle end-time behavior.
        pass

# --- End Giveaway ---
def get_giveaway_by_id(giveaway_id: str) -> Optional[Giveaway]:
    giveaways = load_giveaways()
    for g in giveaways:
        if g.id == giveaway_id:
            return g
    return None


def update_giveaway(giveaway: Giveaway):
    """Save/update a single giveaway in storage."""
    giveaways = load_giveaways()
    for i, g in enumerate(giveaways):
        if g.id == giveaway.id:
            giveaways[i] = giveaway
            save_giveaways(giveaways)
            return
    # not found -> append
    giveaways.append(giveaway)
    save_giveaways(giveaways)


def end_giveaway(giveaway_id: str) -> List[int]:
    """Mark giveaway inactive and pick winners from participants.

    - This is idempotent: if winners already selected it will return them.
    - Returns the list of winner user IDs.
    """
    giveaways = load_giveaways()
    for g in giveaways:
        if g.id == giveaway_id:
            # If already ended / winners chosen, return existing winners
            if not g.active and g.winner_ids:
                return g.winner_ids

            g.active = False
            eligible = list(dict.fromkeys(g.participants))  # remove duplicates, preserve ordering
            if len(eligible) < g.winners:
                # Not enough participants: no winners chosen
                g.winner_ids = []
                update_giveaway(g)
                return []

            from random import sample
            winners = sample(eligible, g.winners)
            g.winner_ids = winners
            update_giveaway(g)
            return winners

    return []

# --- Reroll ---
def reroll_giveaway(giveaway_id: str, exclude: List[int]) -> List[int]:
    g = get_giveaway_by_id(giveaway_id)
    if not g:
        return []

    eligible = [uid for uid in g.participants if uid not in exclude]
    if len(eligible) < g.winners:
        return []

    from random import sample
    winners = sample(eligible, g.winners)
    g.winner_ids = winners
    update_giveaway(g)
    return winners

# --- APScheduler Job ---
def check_giveaway_jobs():
    delete_expired_giveaways()
    giveaways = load_giveaways()
    now = datetime.utcnow()
    for g in giveaways:
        if g.active and g.end_time <= now:
            end_giveaway(g.id)

# --- Scheduler Setup ---
def setup_scheduler():
    # Add the periodic checker job only if it doesn't exist already
    if not scheduler.get_job('giveaway_checker'):
        scheduler.add_job(check_giveaway_jobs, 'interval', minutes=2, id='giveaway_checker', replace_existing=True)

    # Start scheduler only if it's not running and an event loop exists
    if scheduler.running:
        return

    try:
        # Ensure we have a running loop before starting the AsyncIO scheduler
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop available yet — caller should start the scheduler later
        return

    scheduler.start()


# --- Embed helpers (UI helpers used by the bot cog / slash command) ---
DEFAULT_THUMBNAIL_EMOJI = "<:psg:1442958094891221074>"
DEFAULT_THUMBNAIL_URL = "https://cdn.discordapp.com/emojis/1442958094891221074.png?v=1"


def _thumbnail_url_from_custom_emoji(emoji: str) -> str:
    """Convert a custom emoji string like '<:name:12345>' to a CDN url.
    Falls back to DEFAULT_THUMBNAIL_URL if parsing fails.
    """
    if not emoji or ':' not in emoji:
        return DEFAULT_THUMBNAIL_URL
    try:
        # emoji format: <a:name:id> or <:name:id>
        parts = emoji.strip('<>').split(':')
        _name = parts[-2]
        eid = parts[-1]
        return f"https://cdn.discordapp.com/emojis/{eid}.png?v=1"
    except Exception:
        return DEFAULT_THUMBNAIL_URL


def seconds_to_readable(seconds: int) -> str:
    """Convert a duration in seconds to a human-readable string.

    Examples: 43200 -> "12 hours", 86400 -> "1 day", 172800 -> "2 days"
    """
    try:
        secs = int(seconds)
    except Exception:
        return str(seconds)

    # Prefer days if >= 24 hours
    if secs >= 86400:
        days = secs // 86400
        return f"{days} day" + ("s" if days != 1 else "")

    # fallback to hours
    hours = secs // 3600
    if hours < 1:
        # less than 1 hour: show minutes
        minutes = max(1, secs // 60)
        return f"{minutes} minute" + ("s" if minutes != 1 else "")
    return f"{hours} hour" + ("s" if hours != 1 else "")


def default_embed(title: str, description: Optional[str] = None, color: int = 0x341a6b) -> nextcord.Embed:
    """Create a default giveaway embed with the standard thumbnail and description.

    This centralizes thumbnail/description behavior so the UI is always consistent.
    """
    desc = description or "A new Giveaway has just started.\nReact with 🎉 now to enter."
    embed = nextcord.Embed(title=title, description=desc, color=color)
    embed.set_thumbnail(url=_thumbnail_url_from_custom_emoji(DEFAULT_THUMBNAIL_EMOJI))
    return embed


def build_start_embed(g: Giveaway) -> nextcord.Embed:
    """Build an embed for a newly started giveaway from a Giveaway object."""
    embed = default_embed("🎉 Giveaway Started! 🎉")
    embed.add_field(name="Prize", value=g.prize, inline=False)
    embed.add_field(name="Host", value=(f"<@{g.host_id}>" if getattr(g, 'host_id', None) else g.host_name), inline=True)
    # duration might be stored as seconds or readable; try to be helpful
    embed.add_field(name="Duration", value=(seconds_to_readable(g.duration_seconds) if getattr(g, 'duration_seconds', None) else "Unknown"), inline=True)
    embed.add_field(name="Winners", value=str(g.winners), inline=True)
    embed.add_field(name="Winner(s)", value=(", ".join(f"<@{w}>" for w in g.winner_ids) if g.winner_ids else "TBD"), inline=False)
    if getattr(g, 'message', None):
        embed.add_field(name="Message", value=str(g.message), inline=False)
    if getattr(g, 'end_time', None):
        embed.set_footer(text=f"Ends: {g.end_time.strftime('%Y-%m-%d %H:%M UTC')}")
    return embed


def update_embed_winners(embed: nextcord.Embed, winners: Optional[Iterable[int]], title_override: Optional[str] = None) -> nextcord.Embed:
    """Remove any existing Winner(s) field and add a fresh one with `winners`.

    `winners` can be None/empty -> will put 'No winners' or 'TBD'.
    """
    if not isinstance(embed, nextcord.Embed):
        # keep function safe when callers pass the wrong thing
        embed = default_embed(title_override or "🎉 Giveaway Ended 🎉", description=None)

    # collect all fields except existing Winner(s)
    fields = [f for f in embed.fields if not (f.name and f.name.lower().startswith('winner'))]
    embed.clear_fields()
    for f in fields:
        if f.name is not None and f.value is not None:
            embed.add_field(name=str(f.name), value=str(f.value), inline=f.inline)

    if winners:
        winner_text = ", ".join(f"<@{w}>" for w in winners)
    else:
        # If winners is an empty list -> 'No winners', if None -> 'TBD'
        winner_text = "No winners" if winners == [] else "TBD"

    embed.add_field(name='Winner(s)', value=winner_text, inline=False)

    # Update title if caller requested an override or we are handling winners
    if title_override is not None:
        embed.title = title_override
    else:
        # sensible default: when updating winners assume the giveaway ended
        embed.title = "🎉 Giveaway Ended 🎉"

    # ensure thumbnail still set
    if not embed.thumbnail or not getattr(embed.thumbnail, 'url', None):
        embed.set_thumbnail(url=DEFAULT_THUMBNAIL_URL)

    return embed


# --- Reaction helpers (async): extract users from message reactions and sample winners ---
async def gather_reaction_user_ids_from_message(channel: nextcord.TextChannel, message_id: int, emoji: str = '🎉', exclude: Optional[Iterable[int]] = None, dedupe: bool = True) -> list:
    """Fetch a message and return a list of user IDs who reacted with `emoji`.

    - Skips bots.
    - `exclude` can be an iterable of user ids to ignore.
    - Returns a deduplicated list preserving reaction order by default.
    """
    if not isinstance(channel, nextcord.TextChannel):
        return []
    try:
        msg = await channel.fetch_message(message_id)
    except Exception:
        return []

    reaction_users = []
    for reaction in msg.reactions:
        if str(getattr(reaction, 'emoji', '')) == emoji:
            try:
                async for u in reaction.users():
                    if getattr(u, 'bot', False):
                        continue
                    reaction_users.append(getattr(u, 'id', None))
            except Exception:
                continue

    # Apply excludes and dedupe while preserving order
    seen = set()
    excluded = set(exclude) if exclude is not None else set()
    eligible = []
    for uid in reaction_users:
        if uid is None:
            continue
        if uid in excluded:
            continue
        if dedupe and uid in seen:
            continue
        seen.add(uid)
        eligible.append(uid)

    return eligible


async def pick_reaction_winners(channel: nextcord.TextChannel, message_id: int, exclude: Optional[Iterable[int]], count: int, emoji: str = '🎉') -> list:
    """Return `count` sampled winner ids from reactions, excluding `exclude`.

    Returns an empty list if not enough eligible participants.
    """
    eligible = await gather_reaction_user_ids_from_message(channel, message_id, emoji=emoji, exclude=exclude, dedupe=True)
    if len(eligible) < count:
        return []

    from random import sample
    return sample(eligible, count)
