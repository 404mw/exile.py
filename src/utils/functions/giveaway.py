import json
import os
from datetime import datetime, timedelta
from typing import List, Optional
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.utils.types.giveaway import Giveaway, GiveawayJob, RerollPool

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
