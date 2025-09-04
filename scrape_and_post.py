import os
import requests
from datetime import datetime

# خواندن اطلاعات از سکرت‌های گیت‌هاب
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
MESSAGE_ID_FILE = "last_message_id.txt" 

def get_table_from_football360():
    """جدول لیگ را از API داخلی و پایدار سایت Football360 دریافت می‌کند."""
    # این لینک، منبع اصلی داده‌های جدول در خود سایت است
    url = "https://api.football360.ir/api/league/standings/a904ddf6-5df3-43b8-b5fb-15601e4a78ac"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        standings = data.get("data", {}).get("standings", [])[0].get("rows", [])

        if not standings:
            return "❌ داده‌ای برای جدول لیگ در API سایت Football360 یافت نشد."
        
        season = data.get("data", {}).get("season", {}).get("name", "")
        table_text = f"📊 **جدول لیگ برتر خلیج فارس - {season}**\n\n"
        table_text += "`"
        table_text += "R | تیم         | B | W | D | L | Pts\n"
        table_text += "-------------------------------------\n"

        for team in standings:
            rank = team.get("rank", "-")
            name = team.get("team", {}).get("name", "تیم نامشخص")
            played = team.get("played", "-")
            wins = team.get("win", "-")
            draws = team.get("draw", "-")
            losses = team.get("loss", "-")
            points = team.get("point", "-")

            table_text += f"{str(rank):<2}| {name:<12}| {str(played):<2}| {str(wins):<2}| {str(draws):<2}| {str(losses):<2}| {str(points):<3}\n"
        
        table_text += "`"
        return table_text
    except Exception as e:
        print(f"Error getting data from Football360 API: {e}")
        return f"⚠️ خطایی در دریافت اطلاعات از API سایت Football360 رخ داد:\n`{e}`"

def send_or_edit_telegram_message(message):
    """پیام را به کانال تلگرام ارسال یا ویرایش می‌کند."""
    last_message_id = None
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, "r") as f:
            content = f.read().strip()
            if content.isdigit(): last_message_id = int(content)

    payload = { "chat_id": CHANNEL_ID, "text": message, "parse_mode": "Markdown" }
    
    if last_message_id:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        payload["message_id"] = last_message_id
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(url, data=payload)
    response_json = response.json()

    if not response_json.get("ok") and last_message_id:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload.pop("message_id")
        response = requests.post(url, data=payload)
        response_json = response.json()

    if response_json.get("ok"):
        new_message_id = response_json["result"]["message_id"]
        with open(MESSAGE_ID_FILE, "w") as f: f.write(str(new_message_id))
        print(f"Message sent/edited successfully! ID: {new_message_id}")
    else:
        print(f"Failed to send/edit message: {response.text}")

if __name__ == "__main__":
    table = get_table_from_football360()
    send_or_edit_telegram_message(table)
