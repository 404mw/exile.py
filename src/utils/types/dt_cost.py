from pydantic import BaseModel

class Costs(BaseModel):
    """
    Pydantic model representing the costs for a Divine Temple rank.
    
    Attributes:
        name (str): Name of the rank (e.g., 'origin', 'surge')
        gems (int): Aurora Gems cost
        spiritvein (int): Scattered Spiritvein Shards cost
        cots (int): Crystals of Transcendence cost
        stellars (int): Stellar Shards cost
    """
    name: str = "unknown"
    gems: int = 0
    spiritvein: int = 0
    cots: int = 0
    stellars: int = 0