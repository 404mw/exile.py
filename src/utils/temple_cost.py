"""
Temple Level Cost Data.
Contains resource requirements for each temple level (1-22).
Each level requires:
- Aurora Gems
- Scattered Spiritvein Shards
"""

from typing import List
from .types.temple_cost import Temple


temple_cost: List[Temple] = [
    Temple(
        level = 1,
        gem = 5,
        spiritvein = 197236
    ),
    Temple(
        level = 2,
        gem = 15,
        spiritvein = 591708
    ),
    Temple(
        level = 3,
        gem = 34,
        spiritvein = 1343344
    ),
    Temple(
        level = 4,
        gem = 54,
        spiritvein = 2136108
    ),
    Temple(
        level = 5,
        gem = 75,
        spiritvein = 2966180
    ),
    Temple(
        level = 6,
        gem = 98,
        spiritvein = 3876980
    ),
    Temple(
        level = 7,
        gem = 123,
        spiritvein = 4866216
    ),
    Temple(
        level = 8,
        gem = 151,
        spiritvein = 5975780
    ),
    Temple(
        level = 9,
        gem = 183,
        spiritvein = 7242216
    ),
    Temple(
        level = 10,
        gem = 217,
        spiritvein = 8587852
    ),
    Temple(
        level = 11,
        gem = 256,
        spiritvein = 10157552
    ),
    Temple(
        level = 12,
        gem = 312,
        spiritvein = 12374388
    ),
    Temple(
        level = 13,
        gem = 372,
        spiritvein = 14774924
    ),
    Temple(
        level = 14,
        gem = 443,
        spiritvein = 17611060
    ),
    Temple(
        level = 15,
        gem = 520,
        spiritvein = 20658732
    ),
    Temple(
        level = 16,
        gem = 612,
        spiritvein = 24325704
    ),
    Temple(
        level = 17,
        gem = 766,
        spiritvein = 30421048
    ),
    Temple(
        level = 18,
        gem = 890,
        spiritvein = 35354456
    ),
    Temple(
        level = 19,
        gem = 1044,
        spiritvein = 41449800
    ),
    Temple(
        level = 20,
        gem = 1104,
        spiritvein = 43850336
    ),
    Temple(
        level = 21,
        gem = 1258,
        spiritvein = 49945680
    ),
    Temple(
        level = 22,
        gem = 1532,
        spiritvein = 60842096
    ),
]