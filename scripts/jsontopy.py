import json
from decimal import Decimal, getcontext

getcontext().prec = 100  # high precision for safety

INPUT_JSON = "seHP.json"
OUTPUT_PY = "generated_data.py"

THRESHOLD = Decimal("1e14")


def format_decimal(value: Decimal) -> str:
    """
    Returns a Decimal literal string.
    Uses scientific notation with exactly 13 decimal places if >= 1e14.
    """
    if value >= THRESHOLD:
        sci = f"{value:.13E}".replace("E", "e")
        return f"Decimal('{sci}')"
    else:
        return f"Decimal('{value}')"


with open(INPUT_JSON, "r", encoding="utf-8") as f:
    raw = json.load(f)

lines = []
lines.append("from decimal import Decimal\n")
lines.append("data = {\n")

for k, v in raw.items():
    key = k
    value = Decimal(str(v))

    key_str = key
    value_str = format_decimal(value)

    lines.append(f"    {key_str}: {value_str},\n")

lines.append("}\n")

with open(OUTPUT_PY, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"Generated {OUTPUT_PY}")
