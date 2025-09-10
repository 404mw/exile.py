from typing import List
from pydantic import BaseModel

class MsgCommand(BaseModel):
    name: str
    aliases: List[str]
    responses: List[str]