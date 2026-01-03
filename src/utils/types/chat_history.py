# -*- coding: utf-8 -*-

"""
This module defines the Pydantic models for storing user chat history.
"""

from pydantic import BaseModel, Field, RootModel
from typing import Dict, List


class ChatHistory(BaseModel):
    """
    Represents a user's chat history.

    Attributes:
        discord_username (str): The user's Discord username.
        server_nickname (str | None): The user's server-specific nickname.
        queries (List[str]): A list of the user's recent queries.
    """
    discord_username: str
    server_nickname: str | None = None
    queries: List[str] = Field(default_factory=list, max_length=5)


class ChatHistories(RootModel[Dict[str, ChatHistory]]):
    """
    Represents all users' chat histories as a dictionary keyed by user ID.
    """
    root: Dict[str, ChatHistory] = Field(default_factory=dict)
