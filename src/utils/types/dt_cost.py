from pydantic import BaseModel

class Costs(BaseModel):
    name: str = "unknown"
    gems: int = 0
    spiritvein: int = 0
    cots: int = 0
    stellars: int = 0