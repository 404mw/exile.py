from pydantic import BaseModel

class Temple(BaseModel):
    """
    Pydantic model representing the resource requirements for a temple level.
    
    Attributes:
        level (int): Temple level (1-22)
        gem (int): Required Aurora Gems
        spiritvein (int): Required Scattered Spiritvein Shards
    """
    level: int
    gem: int
    spiritvein: int
