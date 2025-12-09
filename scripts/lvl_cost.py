import json

def generate_levels(max_level=250):
    levels = {}
    cumulative = 0

    for level in range(1, max_level + 1):
        # Hybrid XP requirement: fast start, gradual climb
        xp_required = round(100 * level + (level ** 3) * 3)

        cumulative += xp_required
        levels[level] = cumulative   # flat JSON: int → int

    return levels

data = generate_levels()

with open("levels.json", "w") as f:
    json.dump(data, f, indent=4)

print("Generated levelCosts.json.")
