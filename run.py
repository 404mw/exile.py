#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal launcher for Exile.py Discord bot.

This script can be run from any directory and will correctly set up
the Python path to import the bot modules. This solves issues where
the bot is run from parent directories (e.g., 2 directories up).

Usage:
    python run.py                    # Run from exile.py directory
    python exile.py/run.py          # Run from Projects directory
    python Projects/exile.py/run.py # Run from any parent directory
"""

import os
import sys
from pathlib import Path

def main():
    # Get the absolute path to this script's directory (the exile.py folder)
    script_dir = Path(__file__).parent.resolve()

    # Ensure the exile.py directory is in the Python path
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    # Change working directory to the bot's root
    # This ensures relative file paths (like data/awaPool.json) work correctly
    os.chdir(script_dir)

    print(f"Working directory set to: {os.getcwd()}")
    print(f"Python path includes: {script_dir}")

    # Import and run the bot
    # We do this after setting up the path
    try:
        import bot
    except ImportError as e:
        print(f"Error importing bot: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
