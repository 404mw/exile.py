# -*- coding: utf-8 -*-

"""
This module implements the `/ask` slash command, which allows users to ask
questions that are answered by the bot's AI agent.
"""

import nextcord
from nextcord.ext import commands
from agents import Agent, ModelSettings, Runner
from src.agent.tool_caller import tool_agent
from src.utils.config import config
from src.utils.functions.chat_history import update_chat_history
from src.utils.types.chat_history import ChatHistory
import os
from dotenv import load_dotenv
import re

load_dotenv()
MODEL = os.getenv("OPENAI_MODEL")


class Ask(commands.Cog):
    """
    A cog that handles the `/ask` slash command.
    """

    def __init__(self, bot: commands.Bot):
        """
        Initialize the Ask cog.

        Args:
            bot (commands.Bot): The bot instance this cog is being added to.
        """
        self.bot = bot

    @nextcord.slash_command(
        name="ask",
        description="I'm still learning but I'll try my best.",
        guild_ids=[config.exile_server_id, config.test_server_id]
    )
    async def ask(
        self,
        interaction: nextcord.Interaction,
        query: str = nextcord.SlashOption(
            name="query",
            description="Ask a general or IH related question.",
            required=True
        ),
    ):
        """
        Handle the `/ask` slash command.

        Args:
            interaction (Interaction): The interaction object.
            query (str): The user's question.
        """
        try:
            # ============================================================================
            # COMMAND PROCESSING
            # ============================================================================

            # Defer the response to allow time for the agent to process the query.
            await interaction.response.defer()

            if not interaction.user:
                await interaction.followup.send(
                    "⚠️ Could not identify you, sorry.", ephemeral=True
                )
                return

            user_id = interaction.user.id
            discord_username = interaction.user.name
            server_nickname = getattr(interaction.user, 'display_name', None)
            
            history = update_chat_history(user_id, query, discord_username, server_nickname)

            # Create a more descriptive history string for the agent, newest first.
            reversed_queries = reversed(history.queries)
            history_list = [f"{i+1}. {q}" for i, q in enumerate(reversed_queries)]
            history_str = "\n".join(history_list)

            # Get user's preferred name, sanitize it, and default if necessary
            raw_user_name = getattr(interaction.user, 'display_name', None) or interaction.user.name
            sanitized_user_name = re.sub(r'[^a-zA-Z0-9]', '', raw_user_name)
            user_display_name = sanitized_user_name if sanitized_user_name else "Wandering Exiler"

            chat_agent_instructions = f"""
System:
You are a helpful and sarcastic discord bot. Plain string no markdown.
You must never reply with the history unless the user asks for it.
The user you are talking to is named {user_display_name}.

Here is the user's recent query history (from newest to oldest):
{history_str}
"""

            chat_agent = Agent(
                name="Chat Agent",
                instructions=chat_agent_instructions,
                model=MODEL,
                model_settings=ModelSettings(max_tokens=200)
            )

            nav_agent = Agent(
                name="Navigator Agent",
                instructions="""
1- Do not answer queries yourself.
2- Classify each query:
  - If it’s a general question, handoff to chat_agent.
  - If it’s game-related data, handoff to tool_caller.
3- Always route, never respond directly.
""",
                handoffs=[tool_agent, chat_agent]
            )

            # Run the navigator agent with the user's query.
            result = await Runner.run(starting_agent=nav_agent, input=query)
            output = str(result.final_output)

            # ============================================================================
            # RESPONSE
            # ============================================================================

            # Send the agent's response as a follow-up message.
            await interaction.followup.send(output)

        except Exception as e:
            # ============================================================================
            # ERROR HANDLING
            # ============================================================================

            # Print the error to the console for debugging purposes.
            print(e)

            # Send an ephemeral error message to the user.
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "⚠️ Something went wrong, kindly try again.", ephemeral=True
                )
            else:
                await interaction.followup.send(
                    "⚠️ Something went wrong, kindly try again.", ephemeral=True
                )


def setup(bot: commands.Bot):
    """
    Set up the Ask cog.

    Args:
        bot (commands.Bot): The bot instance to add the cog to.
    """
    bot.add_cog(Ask(bot))
