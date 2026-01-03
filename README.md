# Exile.py Discord Bot

Exile.py is a feature-rich Discord bot designed for the "Idle Heroes" gaming community. Its core functionality is a sophisticated, multi-tiered leveling system that rewards users with experience points (XP) based on their server activity. The bot also includes a variety of slash commands for utility and entertainment.

## Features

*   **Advanced Leveling System:**
    *   Users gain XP for messaging in designated channels.
    *   A complex, four-tier XP calculation system featuring:
        *   Static XP bonuses.
        *   Normal XP multipliers.
        *   Level-based multipliers.
        *   A final "true" multiplier.
    *   Highly configurable via a central `config.py` file.
*   **User Statistics:**
    *   Commands to check user level and rank (`/user_stats`).
    *   A server-wide leaderboard (`/leaderboard`).
*   **Game-Specific Tools:**
    *   Calculators for in-game mechanics like "Grim" (`/grim_calc`).
*   **Utility and Fun:**
    *   Ask questions with an integrated AI (`/ask`).
    *   Standard bot commands like `/ping`.
*   **Modular and Extendable:**
    *   A clean and organized file structure makes it easy to add new commands and features.

## Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/404mw/exile.py.git
    cd exile.py
    ```
2.  **Install dependencies:**
    This project uses `uv` for package management.
    ```bash
    uv sync 
    ```
3.  **Create a `.env` file:**
    Copy the `.env.sample` file to a new file named `.env`.
    ```bash
    cp .env.sample .env
    ```
    Edit the `.env` file and add your Discord bot token:
    ```
    DISCORD_TOKEN=your_bot_token_here
    ```
4.  **Run the bot:**
    ```bash
    uv run bot.py
    ```

## Configuration

The bot's behavior, especially the leveling system, can be customized by editing the `src/utils/config.py` file. This file contains pydantic classes safe configuration.

Key configuration options include:

*   **XP Bonuses (`XpBonus`):** Set static XP values for different actions.
*   **XP Multipliers (`XpMultiplier`):** Define multipliers for XP calculations.
*   **Roles (`roles`):** Specify role IDs for different user levels.
*   **Channels (`channels`):** Configure which channels are used for leveling and other features.

## Usage

The bot primarily uses slash commands. Once the bot is running and invited to your Discord server, you can see a list of all available commands by typing `/` in a text channel.

## Data Storage

The bot stores user levels and other data in JSON files located in the `data/` directory.

*   `user_levels.json`: Contains the XP and level for each user.
*   `levelCosts.json`: Stores the cumulative XP required for each level.

**Important:** It is recommended to back up these files regularly to prevent data loss.

## Future Work

*   **Database Migration:** The current data storage system using flat JSON files is simple but can be prone to data loss and race conditions, especially at scale. Migrating to a more robust database system like SQLite or PostgreSQL would significantly improve data integrity and performance.
*   **Expanded Command Suite:** Continue to add more useful and entertaining commands for the "Idle Heroes" community.
*   **Enhanced AI Integration:** The `/ask` command can be further developed to provide more context-aware and helpful responses.

## Contributing

Contributions are welcome! If you have any ideas for new features or improvements, please open an issue or submit a pull request.

## License

This project is currently unlicensed. Please add a license file if you wish to distribute it.
