import json
with open("levels.json", "r") as f:
    levels = json.load(f)

print(levels["level1"])