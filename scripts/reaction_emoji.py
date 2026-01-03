import nextcord
import aiohttp
import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("TOKEN")

GUILD_ID = 1190725475799146507
CHANNEL_ID = 1190747225425457292
MESSAGE_ID = 1454924834617163840

INTENTS = nextcord.Intents.default()
INTENTS.messages = True
INTENTS.guilds = True
INTENTS.reactions = True

client = nextcord.Client(intents=INTENTS)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    guild = client.get_guild(GUILD_ID)
    if guild is None:
        print("Guild not found")
        await client.close()
        return

    channel = guild.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found")
        await client.close()
        return

    try:
        message = await channel.fetch_message(MESSAGE_ID)
    except Exception as e:
        print(f"Failed to fetch message: {e}")
        await client.close()
        return

    os.makedirs("emojis", exist_ok=True)

    async with aiohttp.ClientSession() as session:
        for reaction in message.reactions:
            emoji = reaction.emoji

            # We only want animated custom emojis
            if getattr(emoji, "id", None) and emoji.animated:
                url = f"https://cdn.discordapp.com/emojis/{emoji.id}.gif"
                filename = f"emojis/{emoji.name}_{emoji.id}.gif"

                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(filename, "wb") as f:
                            f.write(await resp.read())
                        print(f"Downloaded: {filename}")
                    else:
                        print(f"Failed to download {emoji.name}")

    print("Done.")
    await client.close()


client.run(BOT_TOKEN)
