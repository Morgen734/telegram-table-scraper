import requests
import json
import os

# متغیرها
BOT_TOKEN = os.getenv("BOT_TOKEN")  # توکن بات
CHAT_ID = os.getenv("CHAT_ID")      # chat_id کانال (مثلاً -1001234567890)

def load_table():
    with open("table.json", "r", encoding="utf-8") as f:
        return json.load(f)

def format_table(data):
    lines = ["🏆 جدول لیگ برتر خلیج فارس:"]
    for row in data["table"]:
        lines.append(f"{row['position']}. {row['team']} - {row['points']} امتیاز")
    return "\n".join(lines)

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    r = requests.post(url, json=payload)
    r.raise_for_status()

if __name__ == "__main__":
    table = load_table()
    msg = format_table(table)
    send_message(msg)
