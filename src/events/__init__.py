"""
Event loader for Discord bot events.
Dynamically loads all event handlers from separate files.
"""
import os
import importlib

def setup(bot):
    """Dynamically load all event handler modules"""
    events_dir = os.path.dirname(__file__)
    
    for filename in os.listdir(events_dir):
        if filename.endswith(".py") and filename not in ["__init__.py"]:
            module_name = f"src.events.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "setup"):
                    module.setup(bot)
            except Exception as e:
                print(f"Error loading event module {module_name}: {e}")