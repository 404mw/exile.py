# Gemini Agent Development Guide for Exile.py

This document provides instructions for the Gemini agent on how to correctly modify and extend the Exile.py project. Adhering to these guidelines is crucial for maintaining the project's architectural integrity.

## Core Principles

The bot's architecture is built on four core principles:

1. **Modularity**: Features are self-contained and separated by concern. New commands and events are added in their own files as Cogs.

2. **Configurability**: Bot settings are centralized in `src/utils/config.py` and are not hardcoded.

3. **Scalability**: The structure is designed for growth. Data access logic is centralized in `src/utils/functions/` to simplify a future migration to a proper database.

4. **Code Quality and Documentation**: The codebase must be thoroughly documented to ensure it is readable, maintainable, and type-safe.
    - **General Documentation**: All Python files, classes, and functions/methods must have docstrings. Use comments to explain the *why* behind complex logic, not just the *what*. The style in `@src/slash_commands/ask.py` is the project-wide reference.
    - **Pydantic for Type Safety**: All data models in `src/utils/types/` must use `pydantic.BaseModel` for validation. These models require a special `Attributes:` section in their class docstring to explain each field.
    - **Static Analysis**: All code must pass static analysis checks without any errors or warnings. This includes type checking and linting to catch potential issues early. Ensure that there are no Pylance (or equivalent) errors before finalizing changes.
    - **Architectural Documentation**: Any significant feature addition or architectural change must be documented in the `docs/` directory. This ensures that the project's documentation stays up-to-date with the codebase.

## File and Folder Structure

When adding or modifying files, strictly follow this structure:

- **`bot.py`**: This is the main entry point. Its primary role is to load configurations and all command/event cogs from the `src/` directory. Do not add command logic directly to this file.

- **`data/`**: This directory is exclusively for data persistence files (e.g., `user_levels.json`).

- **`src/`**: All Python source code resides here.

  - **`src/agent/`**: Contains all logic related to the conversational AI, including the `/ask` command.
    - **`tools/`**: This package contains the tools for the tool-calling agent.
  - **`src/events/`**: Contains event handlers (`on_ready`, `on_message`, etc.). **Each event must be in its own separate file** as a self-contained Cog.
    - **`src/message_commands/`**: Contains context menu commands.
    - **`src/slash_commands/`**: Contains all slash commands. **Each command or logically grouped set of commands must be in its own separate file** as a Cog.
    - **`src/utils/`**: A package for shared code.
      - **`config.py`**: The single source of truth for all bot configurations.
      - **`functions/`**: Contains reusable business logic (e.g., `leveling.py`, `user_level.py`).
      - **`types/`**: Contains custom Pydantic type definitions.

## How to Add New Features

### Adding a New Slash Command

1. Create a new Python file inside the `src/slash_commands/` directory (e.g., `src/slash_commands/my_new_command.py`).
2. Inside the new file, define a class that inherits from `nextcord.ext.commands.Cog`.
3. Add your new slash command as a method within this class, decorated with `@nextcord.slash_command()`.
4. Follow the documentation principle for all new code.
5. Add a `setup(bot)` function at the end of the file to register the cog. The bot will load it automatically.

### Adding a New Event Handler

1. Create a new Python file inside the `src/events/` directory (e.g., `src/events/on_new_event.py`).
2. Define a class that inherits from `nextcord.ext.commands.Cog`.
3. Add your event handler as a method within this class, decorated with `@commands.Cog.listener()`.
4. Follow the documentation principle for all new code.
5. Add a `setup(bot)` function at the end of the file.
