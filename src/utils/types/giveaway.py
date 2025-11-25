from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Giveaway(BaseModel):
    id: str
    prize: str
    host_id: int
    host_name: str
    winners: int
    duration_seconds: int
    start_time: datetime
    end_time: datetime
    message: Optional[str] = None
    mention: bool = False
    channel_id: int
    active: bool = True
    participants: List[int] = Field(default_factory=list)
    winner_ids: List[int] = Field(default_factory=list)
    # message_id stores the Discord message ID for the giveaway post so we
    # can edit / update it when the giveaway ends or when rerolls occur.
    message_id: Optional[int] = None

class GiveawayJob(BaseModel):
    giveaway_id: str
    job_id: str
    end_time: datetime

class RerollPool(BaseModel):
    giveaway_id: str
    previous_winners: List[int] = Field(default_factory=list)
    eligible: List[int] = Field(default_factory=list)
