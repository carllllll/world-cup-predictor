import json

with open("data/team_profiles.json", encoding="utf-8") as f:
    profiles = json.load(f)

team = "Argentina"
p = profiles[team]

print("Flag:", p.get("flag"))
print("Coach:", p.get("coach"))
print("Players:", p.get("key_players"))
print("Type:", type(p))