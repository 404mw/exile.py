from pydantic import BaseModel
from typing import List


class History(BaseModel):
    user: str
    system: str

class ChatContext(BaseModel):
    username: str = "unknown"
    history: List[History]
