from pydantic import BaseModel, Field


class Emojis(BaseModel):
    # General
    ping: str = "<:ping:1326194149808144425>"
    gopnik: str = "<:gopnik:1325482731551068170>"
    hp: str = "<:hp:1325816948889747456>"

    # Star Expedition
    se1g: str = "<a:se1g:1353437489708269628>"
    se2g: str = "<a:se2g:1349453030025859123>"

    # Destiny Temple
    origin: str = "<:origin:1332021165073367060>"
    surge: str = "<:surge:1332021150586245140>"
    chaos: str = "<:chaos:1332021096110755975>"
    core: str = "<:core:1332021073977278544>"
    polystar: str = "<:polystar:1332021054763303053>"
    nirvana: str = "<:nirvana:1332021038044676096>"
    gem: str = "<:auroragem:1332031851048472627>"
    spiritvein: str = "<:spiritvein:1333082447772123146>"
    bag: str = "<:bag:1333083225244827698>"

    # Awakenings
    csg: str = "<:csg:1338159695227129956>"
    awakene: str = "<:awakene:1328071268146085969>"
    awakend: str = "<:awakend:1328071247384416286>"
    awakensss: str = "<:awakensss:1329829693968613428>"

    # Grimoire
    grim_essence: str = "<:grim_essence:1447653904002056212>"
    grim_imprint: str = "<:grim_imprint:1447655509628031096>"
    grim_book1: str = "<:grim_book1:1447653930816377036>"

    # Pepe the frog
    point_laugh: str = "<:laugh_point:1356266540739330321>"
    blush_finger: str = "<:blush_finger:1337833082954317885>"
    laugh: str = "<a:laugh:1356266810718027820>"
    party_shake: str = "<a:peepo_partyhat:1377007874777157632>"

    # Roo the Panda
    roo_fire: str = "<a:panda_fire:1337833115225161788>"

class XpBonus(BaseModel):
    """Represents a static XP bonus for a channel or role"""
    id: int
    amount: int = Field(gt=0, description="Amount of XP to add")

class XpMultiplier(BaseModel):
    """Represents an XP multiplier for a role"""
    id: int
    value: float = Field(gt=0.0, description="Multiplier value (e.g., 1.5 for x1.5)")

class XpTrueMultiplier(BaseModel):
    """Represents a true XP multiplier (applied last) for a role"""
    id: int
    value: float = Field(gt=0.0, description="True multiplier value (e.g., 2.0 for x2)")

class Channels(BaseModel):
    
    spam: str = Field(default="bot-spam")
    level: str = Field(default="levels")
    exile_chat: int = Field(default=866773791560040519, description="Exile 7 channel ID")
    xp_bonuses: list[XpBonus] = Field(default=[], description="Channels that grant static XP bonuses")
    xp_multipliers: list[XpMultiplier] = Field(default=[], description="Channels that grant normal XP multipliers")

class Roles(BaseModel):
    giveaway_manager_role: str = Field(default="giveaway manager", description="Role name that can create/reroll giveaways")
    exile_role: int = Field(default=866772888635441162, description="Exile 7 role ID")
    booster_role: int = Field(default=970496362766536756, description="Server boost role ID for XP multiplier")
    
    xp_bonuses: list[XpBonus] = Field(default=[], description="Roles that grant static XP bonuses")
    xp_multipliers: list[XpMultiplier] = Field(default=[], description="Roles that grant normal XP multipliers")
    xp_true_multipliers: list[XpTrueMultiplier] = Field(default=[], description="Roles that grant true XP multipliers (calculated last)")

class Config(BaseModel):
    PREFIX: str = "!"
    test_server_id: int
    exile_server_id: int

    # XP given per message
    base_XP: int = Field(default=35, description="Amount of base given per message")
    level_multiplier_rate: float = Field(default=0.01, description="XP multiplier per user level (e.g., 0.01 = +1% per level)")