from typing import List
from pydantic import BaseModel

class MsgCommand(BaseModel):
    name: str
    aliases: List[str] | None
    responses: List[str]