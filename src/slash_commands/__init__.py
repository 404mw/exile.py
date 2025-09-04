import os
import importlib

def setup(bot):
    for filename in os.listdir(os.path.dirname(__file__)):
        if filename.endswith(".py") and filename not in ["__init__.py"]:
            module_name = f"src.slash_commands.{filename[:-3]}"
            module = importlib.import_module(module_name)
            if hasattr(module, "setup"):
                module.setup(bot)
