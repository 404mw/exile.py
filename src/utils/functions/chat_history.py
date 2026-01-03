# -*- coding: utf-8 -*-

"""
This module provides functions for managing user chat history.
"""

import json
import os
from typing import Optional

from src.utils.types.chat_history import ChatHistories, ChatHistory


HISTORY_FILE = "data/chat_history.json"


def load_all_chat_histories() -> ChatHistories:
    """
    Loads all user chat histories from a single JSON file.

    Returns:
        ChatHistories: An object containing all user chat histories.
    """
    if not os.path.exists(HISTORY_FILE):
        return ChatHistories(root={})

    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return ChatHistories(root=data)
        except (json.JSONDecodeError, TypeError):
            return ChatHistories(root={})


def save_chat_histories(histories: ChatHistories):
    """
    Saves all user chat histories to a single JSON file.

    Args:
        histories (ChatHistories): The chat histories object to save.
    """
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(histories.model_dump_json(indent=2))


def load_user_chat_history(user_id: int) -> Optional[ChatHistory]:
    """
    Loads a specific user's chat history.

    Args:
        user_id (int): The user's ID.

    Returns:
        Optional[ChatHistory]: The user's chat history, or None if it doesn't exist.
    """
    all_histories = load_all_chat_histories()
    return all_histories.root.get(str(user_id))


def update_chat_history(
    user_id: int, query: str, discord_username: str, server_nickname: Optional[str]
) -> ChatHistory:
    """
    Updates a user's chat history with a new query.

    If the user has no existing chat history, a new one is created.
    If the history exceeds 5 queries, the oldest query is removed.

    Args:
        user_id (int): The user's ID.
        query (str): The new query to add.
        discord_username (str): The user's Discord username.
        server_nickname (Optional[str]): The user's server-specific nickname.

    Returns:
        ChatHistory: The updated chat history.
    """
    all_histories = load_all_chat_histories()
    user_id_str = str(user_id)
    
    history = all_histories.root.get(user_id_str)

    if history is None:
        history = ChatHistory(
            discord_username=discord_username,
            server_nickname=server_nickname,
            queries=[],
        )
        all_histories.root[user_id_str] = history

    # Update names in case they have changed
    history.discord_username = discord_username
    history.server_nickname = server_nickname
    
    # Add new query and manage history length
    if len(history.queries) >= 5:
        history.queries.pop(0)
    history.queries.append(query)

    save_chat_histories(all_histories)
    return history
