import nextcord
from nextcord.ext import commands
from src.utils.config import config
import aiohttp
import os
import re

class Upload(commands.Cog):
    """
    Upload Command Cog.
    Provides a slash command to upload media from message links to the media directory.
    """
    
    def __init__(self, bot: commands.Bot):
        """
        Initialize the Upload cog.
        
        Args:
            bot (commands.Bot): The bot instance this cog is being added to
        """
        self.bot = bot

    async def download_media(self, url: str, filename: str, media_dir: str) -> bool:
        """
        Download media from a URL and save it to the media directory.
        
        Args:
            url (str): The URL of the media to download
            filename (str): The name to save the file as
            media_dir (str): The directory to save the file in
            
        Returns:
            bool: True if download was successful, False otherwise
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    file_path = os.path.join(media_dir, filename)
                    with open(file_path, 'wb') as f:
                        f.write(await response.read())
                    return True
        return False

    @nextcord.slash_command(
        name="upload",
        description="Upload media from message links to the media directory",
        guild_ids=[config.test_server_id]
    )
    async def upload(
        self,
        interaction: nextcord.Interaction,
        message_link: str = nextcord.SlashOption(
            name="message_link",
            description="The Discord message link containing the media",
            required=True
        ),
        name: str = nextcord.SlashOption(
            name="name",
            description="The name to save the media file as (include extension like .png, .gif, etc)",
            required=True
        )
    ):
        """
        Upload media from a message link to the media directory.
        
        Args:
            interaction (nextcord.Interaction): The interaction instance
            message_link (str): The Discord message link containing the media
            name (str): The name to save the media file as
        """
        try:
            # Parse message link
            pattern = r"https://discord.com/channels/(\d+)/(\d+)/(\d+)"
            match = re.match(pattern, message_link)
            
            if not match:
                await interaction.response.send_message("Invalid message link format!", ephemeral=True)
                return
                
            guild_id, channel_id, message_id = map(int, match.groups())
            channel = self.bot.get_channel(channel_id)
            
            if not channel or not isinstance(channel, (nextcord.TextChannel, nextcord.Thread)):
                await interaction.response.send_message("Couldn't access the channel or it's not a text channel!", ephemeral=True)
                return
                
            try:
                message = await channel.fetch_message(message_id)
            except nextcord.NotFound:
                await interaction.response.send_message("Couldn't find the message!", ephemeral=True)
                return
            except nextcord.Forbidden:
                await interaction.response.send_message("I don't have permission to read messages in that channel!", ephemeral=True)
                return
            
            if not message:
                await interaction.response.send_message("Couldn't find the message!", ephemeral=True)
                return
                
            # Check for attachments or embeds with image
            media_url = None
            if message.attachments:
                media_url = message.attachments[0].url
            elif message.embeds and message.embeds[0].image:
                media_url = message.embeds[0].image.url
                
            if not media_url:
                await interaction.response.send_message("No media found in the message!", ephemeral=True)
                return
                
            # Download the media
            media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "media")
            
            await interaction.response.defer()
            
            success = await self.download_media(media_url, name, media_dir)
            
            if success:
                await interaction.followup.send(f"Successfully downloaded media as {name}")
            else:
                await interaction.followup.send("Failed to download media!", ephemeral=True)
                
        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"Error: {str(e)}", ephemeral=True)
            else:
                await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(Upload(bot))