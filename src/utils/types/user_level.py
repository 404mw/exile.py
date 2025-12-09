"""
User level data model for the leveling system.
"""
from pydantic import BaseModel, Field
from typing import Dict

class UserLevel(BaseModel):
    """User leveling data"""
    user_id: int
    username: str
    xp: int = Field(default=0, description="Total experience points")
    level: int = Field(default=1, description="Current level")
