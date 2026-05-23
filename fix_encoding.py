import json

with open("data/team_profiles.json", encoding="utf-8-sig") as f:
    data = json.load(f)

with open("data/team_profiles.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Done! File re-saved with correct UTF-8 encoding.")