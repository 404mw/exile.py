import uuid
from datetime import datetime, timedelta

import nextcord
from nextcord import Interaction, SlashOption,Embed, ButtonStyle
from nextcord.ext import commands
import asyncio

from nextcord.ui import View, Button

from src.utils.functions.giveaway import (
	load_giveaways, save_giveaways, delete_expired_giveaways,
	get_active_giveaway, get_giveaway_by_id, update_giveaway, start_giveaway,
	end_giveaway, reroll_giveaway, setup_scheduler,
	default_embed, build_start_embed, update_embed_winners
    , gather_reaction_user_ids_from_message, pick_reaction_winners
)
from src.utils.types.giveaway import Giveaway

def duration_to_seconds(duration: str) -> int:
	mapping = {
		"12 hours": 43200,
	    "1 day": 86400,
	    "2 days": 172800,
	    "3 days": 259200,
		"7 days": 604800,
	}
	return mapping.get(duration, 86400)
# permission helper removed — we check admin/owner inline in the command
class GiveawayView(View):
	def __init__(self, giveaway_id, host_id, ended: bool = False):
		super().__init__(timeout=None)
		self.giveaway_id = giveaway_id
		self.host_id = host_id
		# If the giveaway has ended, the reroll button should be enabled.
		# We'll set that dynamically (buttons are available on the view via
		# self.children) — by default they are created disabled/enabled
		# according to the decorator settings.
		if ended:
			# enable any reroll button we find
			for child in self.children:
				if isinstance(child, Button) and getattr(child, 'label', None) == 'Reroll':
					child.disabled = False
				if isinstance(child, Button) and getattr(child, 'label', None) == 'End Now':
					# already ended, don't allow End Now
					child.disabled = True
		else:
			# remove reroll from the view so it isn't visible until the giveaway
			# has ended — we'll create a new view with the reroll button when
			# the giveaway ends.
			for child in list(self.children):
				if isinstance(child, Button) and getattr(child, 'label', None) == 'Reroll':
					try:
						self.remove_item(child)
					except Exception:
						pass

	@nextcord.ui.button(label="End Now", style=ButtonStyle.danger)
	async def end_now(self, button: Button, interaction: Interaction):
		# Only the bot owner may end early — use the library's is_owner check
		# which correctly identifies the bot owner.
		try:
			is_owner = await interaction.client.is_owner(interaction.user)
		except Exception:
			is_owner = False

		if not is_owner:
			await interaction.response.send_message("Only the bot owner can end the giveaway early.", ephemeral=True)
			return

		# defer early so we won't hit Unknown interaction errors while we fetch/edit
		# messages & perform I/O that can take longer than the interaction window.
		try:
			await interaction.response.defer(ephemeral=True)
		except Exception:
			# already responded or something went wrong - ignore and continue
			pass

		# End the giveaway (pick winners in storage) and then perform the
		# same announcement/edit as the scheduled end (if message exists).
		winners = end_giveaway(self.giveaway_id)
		g = get_giveaway_by_id(self.giveaway_id)

		# If storage had no participants/winners, try to pick from reactions
		if (not winners or len(winners) == 0) and g and g.message_id and interaction.guild:
			try:
				ch = interaction.guild.get_channel(g.channel_id)
				if isinstance(ch, nextcord.TextChannel):
					# use shared helper to sample winners from reactions
					winners_from_reactions = await pick_reaction_winners(ch, g.message_id, [], g.winners)
					if winners_from_reactions:
						winners = winners_from_reactions
						g.winner_ids = winners
						update_giveaway(g)
			except Exception:
				pass

		# Try to edit the original message and announce winners
		if g and g.message_id:
			channel = interaction.guild.get_channel(g.channel_id) if interaction.guild else None
			if isinstance(channel, nextcord.TextChannel):
				try:
					msg = await channel.fetch_message(g.message_id)
					
					# build/modify embed (use helpers to ensure thumbnail/description show)
					embed = msg.embeds[0] if msg.embeds else default_embed("🎉 Giveaway Ended 🎉")
					embed = update_embed_winners(embed, winners)
					await msg.edit(embed=embed, view=GiveawayView(self.giveaway_id, self.host_id, ended=True))
					
				except Exception:
					pass

		# Announce winners in the channel
		if g:
			channel = interaction.guild.get_channel(g.channel_id) if interaction.guild else None
			if channel and winners and isinstance(channel, nextcord.TextChannel):
				mentions = ", ".join(f"<@{w}>" for w in winners)
				await channel.send(f"🎉 Giveaway has ended — congratulations: {mentions}")

		# reply after the long-running work using a followup
		try:
			await interaction.followup.send("Giveaway ended", ephemeral=True)
		except Exception:
			# fallback to direct response if followup fails
			try:
				await interaction.response.send_message("Giveaway ended", ephemeral=True)
			except Exception:
				pass

	@nextcord.ui.button(label="Reroll", style=ButtonStyle.primary, disabled=True)
	async def reroll(self, button: Button, interaction: Interaction):
		# Reroll is only available once the giveaway has ended — fetch the
		# stored giveaway and ensure it's inactive
		g = get_giveaway_by_id(self.giveaway_id)
		if not g or g.active:
			await interaction.response.send_message("No ended giveaway to reroll.", ephemeral=True)
			return

		# Permission: only server mods (manage_guild/admin) or the bot owner may reroll
		if isinstance(interaction.user, nextcord.Member):
			user_member = interaction.user
		else:
			uid = getattr(interaction.user, 'id', None)
			user_member = interaction.guild.get_member(uid) if (interaction.guild and uid is not None) else None
		try:
			is_owner = await interaction.client.is_owner(interaction.user)
		except Exception:
			is_owner = False
		if not user_member and not is_owner:
			await interaction.response.send_message("You do not have permission to reroll this giveaway.", ephemeral=True)
			return
		if not (is_owner or (user_member is not None and (user_member.guild_permissions.manage_guild or user_member.guild_permissions.administrator))):
			await interaction.response.send_message("Only server moderators or the bot owner can reroll.", ephemeral=True)
			return

		# Defer so we don't hit the interaction timeout while doing fetch/edit
		try:
			await interaction.response.defer(ephemeral=True)
		except Exception:
			pass

		prev_winners = g.winner_ids
		new_winners = reroll_giveaway(self.giveaway_id, prev_winners)
		# if reroll returned no winners (participants not stored), try reactions
		if not new_winners and g and g.message_id and interaction.guild:
			try:
				ch = interaction.guild.get_channel(g.channel_id)
				if isinstance(ch, nextcord.TextChannel):
					new_from_reactions = await pick_reaction_winners(ch, g.message_id, prev_winners, g.winners)
					if new_from_reactions:
						new_winners = new_from_reactions
						g.winner_ids = new_winners
						update_giveaway(g)
			except Exception:
				pass
		if not new_winners:
			try:
				await interaction.followup.send("Not enough eligible participants to reroll.", ephemeral=True)
			except Exception:
				try:
					await interaction.response.send_message("Not enough eligible participants to reroll.", ephemeral=True)
				except Exception:
					pass
			return
		# Announce new winners and update the embed message
		channel = None
		if interaction.guild:
			# Only get text channels
			for ch in interaction.guild.text_channels:
				if ch.id == g.channel_id:
					channel = ch
					break
		if channel:
			winner_mentions = ", ".join(f"<@{uid}>" for uid in new_winners)
			if isinstance(channel, nextcord.TextChannel):
				await channel.send(f"🎉 Reroll! New winners: {winner_mentions}")
				# If the original message exists, edit the embed to show new winners
				if g.message_id:
					try:
						msg = await channel.fetch_message(g.message_id)
						embed = msg.embeds[0] if msg.embeds else default_embed("🎉 Giveaway Ended 🎉")
						embed = update_embed_winners(embed, new_winners)
						# Keep reroll enabled after reroll
						await msg.edit(embed=embed, view=GiveawayView(self.giveaway_id, self.host_id, ended=True))
					except Exception:
						pass
		# respond after the longer work
		try:
			await interaction.followup.send("Reroll complete.", ephemeral=True)
		except Exception:
			try:
				await interaction.response.send_message("Reroll complete.", ephemeral=True)
			except Exception:
				pass

def setup(bot: commands.Bot):
	bot.add_cog(GiveawayCog(bot))


class GiveawayCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# reaction winner selection is centralized in src.utils.functions.giveaway


	async def _schedule_end(self, giveaway: Giveaway):
		"""Async helper to wait until the giveaway's end_time then perform
		announcement and message edits using the bot API.
		"""
		now = datetime.utcnow()
		wait_seconds = max(0, (giveaway.end_time - now).total_seconds())
		await asyncio.sleep(wait_seconds)

		# Pick winners (idempotent) and update storage
		winners = end_giveaway(giveaway.id)

		# Fetch the channel early so we can fallback to reactions if needed
		channel = self.bot.get_channel(giveaway.channel_id)

		# If storage had no winners, fallback to reactions on the message
		if (not winners or len(winners) == 0) and giveaway.message_id and channel and isinstance(channel, nextcord.TextChannel):
			try:
				react_winners = await pick_reaction_winners(channel, giveaway.message_id, [], giveaway.winners)
				if react_winners:
					winners = react_winners
					# persist these winners
					g2 = get_giveaway_by_id(giveaway.id)
					if g2:
						g2.winner_ids = winners
						update_giveaway(g2)
			except Exception:
				pass

		# Fetch the channel and original message if available
		channel = self.bot.get_channel(giveaway.channel_id)
		mention_text = ", ".join(f"<@{w}>" for w in winners) if winners else "No winners"

		# Edit original message embed if we have a message id
		if channel and giveaway.message_id and isinstance(channel, nextcord.TextChannel):
			try:
				msg = await channel.fetch_message(giveaway.message_id)
				embed = msg.embeds[0] if msg.embeds else default_embed("🎉 Giveaway Ended 🎉")
				embed = update_embed_winners(embed, winners)
				await msg.edit(embed=embed, view=GiveawayView(giveaway.id, giveaway.host_id, ended=True))
			except Exception:
				pass

		# Announce winners
		if channel and winners:
				if isinstance(channel, nextcord.TextChannel):
					await channel.send(f"🎉 Giveaway ended — congratulations: {mention_text}")

	async def cog_load(self):
		# Start the scheduler after the bot event loop is ready. setup_scheduler is idempotent.
		setup_scheduler()
		# Re-schedule end tasks for any active giveaways on bot startup so we
		# can handle announcement/editing even when the bot was restarted.
		giveaways = load_giveaways()
		now = datetime.utcnow()
		for g in giveaways:
			if g.active and g.end_time > now:
				# schedule the async handler
				try:
					asyncio.create_task(self._schedule_end(g))
				except Exception:
					pass
	@nextcord.slash_command(name="giveaway", description="Start a giveaway event.")
	async def giveaway(
		self,
		interaction: Interaction,
		prize: str = SlashOption(description="Detailed description of the giveaway prize", required=True),
		duration: str = SlashOption(description="Choose the duration of giveaway", required=True, choices=["12 hours", "1 day", "2 days", "3 days", "7 days"]),
		host: nextcord.Member = SlashOption(description="Host (mention a server member)", required=True),
		winners: int = SlashOption(description="Number of winners (max 3)", required=True, min_value=1, max_value=3),
		mention: bool = SlashOption(description="Mention @everyone?", required=False, default=False),
		message: str = SlashOption(description="Custom message to be attached", required=False, default=None)
	):
		# Permission check
		user_id = getattr(interaction.user, "id", None)
		member = interaction.user if isinstance(interaction.user, nextcord.Member) else (interaction.guild.get_member(user_id) if interaction.guild and user_id else None)
		# Permission: allow server admins or the bot owner
		if not member:
			await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
			return

		try:
			owner_check = await self.bot.is_owner(member)
		except Exception:
			owner_check = False

		if not (member.guild_permissions.administrator or owner_check):
			await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
			return

		# Find #giveaway channel (text channels only)
		giveaway_channel = None
		if interaction.guild:
			for ch in interaction.guild.text_channels:
				if ch.name == "giveaway":
					giveaway_channel = ch
					break
		if not giveaway_channel:
			await interaction.response.send_message("The #giveaway channel does not exist.", ephemeral=True)
			return

		delete_expired_giveaways()
		# Check for active giveaway
		if get_active_giveaway():
			await interaction.response.send_message("There is already an active giveaway. Please wait for it to end.", ephemeral=True)
			return

		# Prepare giveaway data
		now = datetime.utcnow()
		duration_sec = duration_to_seconds(duration)
		end_time = now + timedelta(seconds=duration_sec)
		giveaway_id = str(uuid.uuid4())
		giveaway_obj = Giveaway(
			id=giveaway_id,
			prize=prize,
			host_id=host.id,
			host_name=host.display_name,
			winners=winners,
			duration_seconds=duration_sec,
			start_time=now,
			end_time=end_time,
			message=message,
			mention=mention,
			channel_id=giveaway_channel.id,
			active=True,
			participants=[],
			winner_ids=[],
			message_id=None
		)
		start_giveaway(giveaway_obj)

		# Build embed (use helper to ensure description and thumbnail show)
		embed = build_start_embed(giveaway_obj)

		view = GiveawayView(giveaway_id, member.id)

		# Mention @everyone if requested
		content = "@everyone" if mention else None
		msg = await giveaway_channel.send(content=content, embed=embed, view=view)

		# Reacting with 🎉 so people can enter by reacting — store message id
		# and persist it so we can examine reactions when the giveaway ends.
		try:
			await msg.add_reaction("🎉")
		except Exception:
			# ignore if missing permissions or other errors
			pass

		# Store the message ID so we can edit it later
		giveaway_obj.message_id = msg.id
		update_giveaway(giveaway_obj)

		# Schedule the async end handler so the bot can edit/announce winners
		try:
			asyncio.create_task(self._schedule_end(giveaway_obj))
		except Exception:
			pass

		await interaction.response.send_message(f"Giveaway started in <#{giveaway_channel.id}>!", ephemeral=True)
