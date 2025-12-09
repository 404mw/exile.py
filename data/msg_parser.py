import json

# Load your original JSON
with open("msgCommands.json", "r") as f:
    data = json.load(f)

output = {
    "commands": {},
    "lookup": {}
}

for cmd in data:
    name = cmd["name"]
    aliases = cmd.get("aliases", [])
    responses = cmd["responses"]

    # Store command definition
    output["commands"][name] = {
        "aliases": aliases,
        "responses": responses
    }

    # Add lookup entries (main name + alias all point to root)
    output["lookup"][name] = name
    for alias in aliases:
        output["lookup"][alias] = name

# Save final structured format
with open("output.json", "w") as f:
    json.dump(output, f, indent=2)

print("Generated msgCommands.json successfully.")
