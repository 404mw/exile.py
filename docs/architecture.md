# Exile.py Architecture Guide

This document provides a high-level overview of the Exile.py bot's architecture. It is designed to be modular, configurable, and scalable, making it easy to maintain and extend.

## Project Structure

The project is organized into a `src` directory, which contains all the core logic, and a `data` directory for storing data. This separation of concerns is key to the bot's modularity.

```
exile.py/
├───data/
│   ├───user_levels.json
│   └───...
├───src/
│   ├───agent/
│   ├───events/
│   ├───message_commands/
│   ├───slash_commands/
│   └───utils/
├───bot.py
└───README.md
```

*   **`data/`**: Contains all the bot's data, such as user levels and game-specific information.
*   **`src/`**: The main source code directory.
    *   **`agent/`**: Contains the logic for the bot's conversational AI features (e.g., the `/ask` command).
    *   **`events/`**: Contains event handlers, such as `on_message` for the leveling system and `on_ready`. Each event is in its own file, making it easy to manage.
    *   **`message_commands/`**: Contains message commands (context menu commands).
    *   **`slash_commands/`**: Contains all the slash commands, organized into cogs. Each command or group of related commands is in its own file.
    *   **`utils/`**: Contains utility functions, type definitions, and the main configuration file.
*   **`bot.py`**: The main entry point of the bot. It's responsible for loading the cogs and starting the bot.

## Modularity and Extensibility

The bot is designed to be highly modular, which makes it easy to add new features without affecting existing ones.

### Cogs for Commands

All slash commands are organized into **Cogs**. A cog is a self-contained class that can contain commands, event listeners, and state. This makes it easy to group related commands and features.

For example, the `user_stats.py` and `leaderboard.py` commands are in their own cogs. To add a new command, you can simply create a new file in the `src/slash_commands/` directory with a new cog, and the bot will automatically load it.

### Centralized Configuration

The bot uses a centralized configuration system in `src/utils/config.py`. This file contains all the important settings for the bot, such as server IDs, channel IDs, role IDs, and the parameters for the leveling system.

The configuration is based on typed dataclasses, which provides type safety and makes it easy to see what configuration options are available. This means you can easily customize the bot's behavior without having to dig through the code.

## Scalability

While the bot is currently designed for a single server, its architecture allows for future scaling.

### Data Persistence

Currently, the bot uses JSON files for data persistence. This is simple and works well for small to medium-sized servers. However, for larger servers with many users, this approach can become slow and prone to data loss.

As recommended in the main `README.md`, migrating to a more robust database system like **SQLite** or **PostgreSQL** would be a major improvement for scalability and data integrity. The current data access functions in `src/utils/functions/leveling.py` are centralized, which would make this migration relatively straightforward.

### The Agent System

The `src/agent` directory contains the beginnings of a more advanced conversational AI system. This system is designed to be extendable, allowing you to create more complex and intelligent interactions with the bot. This could be scaled up to use more powerful language models or to integrate with external APIs.

## Conclusion

The Exile.py bot is built on a solid architectural foundation that emphasizes modularity, configurability, and scalability. By leveraging cogs for commands, a centralized configuration system, and a clear project structure, the bot is easy to maintain and extend. With a future migration to a more robust database system, the bot can be scaled to serve even the largest Discord communities.
