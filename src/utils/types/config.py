from pydantic import BaseModel, Field

class AllowedChannels(BaseModel):
    # defaults
    awaken: str = "bot-spam"
    giveaway: str = "1376982644939821229"

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

class Config(BaseModel):
    PREFIX: str = "!"
    allowed_channels: AllowedChannels = Field(default_factory=AllowedChannels)
    emojis: Emojis = Field(default_factory=Emojis)