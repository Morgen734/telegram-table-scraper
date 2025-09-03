import os
import requests

# خواندن اطلاعات از سکرت‌های گیت‌هاب
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
MESSAGE_ID_FILE = "last_message_id.txt" 

def get_table_from_json_api():
    """جدول لیگ را از یک API عمومی و پایدار JSON دریافت می‌کند."""
    # این یک منبع داده عمومی و رایگان برای جدول لیگ ایران است
    url = "https://persianleague-standings.storage.iran.liara.space/standings.json"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        standings = response.json()

        if not standings:
            return "❌ داده‌ای برای جدول لیگ یافت نشد."

        table_text = "📊 **جدول رده‌بندی لیگ برتر خلیج فارس**\n\n"
        table_text += "`"
        table_text += "R | تیم         | B | W | D | L | Pts\n"
        table_text += "-------------------------------------\n"

        for team in standings:
            rank = team.get("rank", "-")
            name = team.get("name_fa", "تیم نامشخص")
            played = team.get("play", "-")
            wins = team.get("win", "-")
            draws = team.get("draw", "-")
            losses = team.get("lose", "-")
            points = team.get("point", "-")

            table_text += f"{str(rank):<2}| {name:<12}| {str(played):<2}| {str(wins):<2}| {str(draws):<2}| {str(losses):<2}| {str(points):<3}\n"
        
        table_text += "`"
        return table_text
    except Exception as e:
        print(f"Error getting data from JSON API: {e}")
        return f"⚠️ خطایی در دریافت اطلاعات از API رخ داد:\n`{e}`"

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
    table = get_table_from_json_api()
    send_or_edit_telegram_message(table)
