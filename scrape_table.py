# scrape_table.py
import requests
import json
import os

LEAGUE_ID = os.getenv("LEAGUE_ID", "4742")   # Persian Gulf Pro League
SEASON = os.getenv("SEASON", "2025-2026")

def get_table():
    url = f"https://www.thesportsdb.com/api/v1/json/1/lookuptable.php?l={LEAGUE_ID}&s={SEASON}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()
    table = []
    if data.get("table"):
        for row in data["table"]:
            table.append({
                "position": int(row.get("intRank") or 0),
                "team": row.get("strTeam"),
                "played": int(row.get("intPlayed") or 0),
                "win": int(row.get("intWin") or 0),
                "draw": int(row.get("intDraw") or 0),
                "loss": int(row.get("intLoss") or 0),
                "goalsFor": int(row.get("intGoalsFor") or 0),
                "goalsAgainst": int(row.get("intGoalsAgainst") or 0),
                "goalDifference": int(row.get("intGoalDifference") or 0),
                "points": int(row.get("intPoints") or 0),
            })
    return {"league": "Persian Gulf Pro League", "season": SEASON, "table": table}

if __name__ == "__main__":
    data = get_table()
    with open("table.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ table.json ساخته شد ({len(data['table'])} تیم).")
