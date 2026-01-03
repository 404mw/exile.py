import nextcord
import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1190790078256119818

MESSAGE_CONTENT = "no missing HP for `/se` anymore <a:yayyyy:1313583615019454514>"

intents = nextcord.Intents.default()
client = nextcord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("Channel not found. Check CHANNEL_ID or bot permissions.")
        await client.close()
        return

    await channel.send(MESSAGE_CONTENT)
    print("Message sent.")

    await client.close()


client.run(BOT_TOKEN)
