# send_to_telegram.py
import os
import json
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def format_table(data):
    lines = [f"📊 {data['league']} ({data['season']})\n"]
    for row in data["table"]:
        lines.append(f"{row['position']}. {row['team']} - {row['points']} pts")
    return "\n".join(lines)

if __name__ == "__main__":
    with open("table.json", encoding="utf-8") as f:
        data = json.load(f)

    text = format_table(data)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    resp.raise_for_status()
    print("✅ جدول به تلگرام ارسال شد.")
