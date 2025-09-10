"""
Divine Temple cost data module.
Contains a list of resource costs for different temple ranks (Origin through Nirvana).
Each rank entry includes:
- Aurora Gems cost
- Spiritvein Shards cost
- COTS (Crystals of Transcendence) cost
- Stellar Shards cost
"""

from typing import List
from .types.dt_cost import Costs

# List of costs for each Divine Temple rank
dt_cost: List[Costs] = [
    Costs(
        name = "origin",
        gems = 5,
        spiritvein = 197-236,
        cots = 420_000,
        stellars = 821_540
    ),
    Costs(
        name = "surge",
        gems = 12,
        spiritvein = 474_436,
        cots = 1_010_000,
        stellars = 1_976_540 
    ),
    Costs(
        name = "chaos",
        gems = 21,
        spiritvein = 830_836,
        cots = 1_760_000,
        stellars = 3_461_540
    ),
    Costs(
        name = "core",
        gems = 32,
        spiritvein = 1_266_436,
        cots = 2_680_000,
        stellars = 5_276_540
    ),
    Costs(
        name = "polystar",
        gems = 45,
        spiritvein = 1_781_236,
        cots = 3_780_000,
        stellars = 7_421_540
    ),
    Costs(
        name = "nirvana",
        gems = 60,
        spiritvein = 2_400_536,
        cots = 5_030_000,
        stellars = 10_000_490
    ),
]