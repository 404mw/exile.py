from pydantic import BaseModel

class Temple(BaseModel):
    level: int
    gem: int
    spiritvein: int
