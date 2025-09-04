import os
import requests
from datetime import datetime

# خواندن اطلاعات از سکرت‌های گیت‌هاب
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
MESSAGE_ID_FILE = "last_message_id.txt" 

def get_table_from_sofascore():
    """جدول لیگ را از API داخلی و پایدار سایت Sofascore دریافت می‌کند."""
    # این لینک، منبع اصلی داده‌های جدول در خود سایت سوفااسکور است
    # شناسه لیگ ایران: 285 / شناسه فصل جاری: 56932
    url = "https://api.sofascore.com/api/v1/unique-tournament/285/season/56932/standings/total"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Cache-Control': 'no-cache',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        standings = data.get("standings", [{}])[0].get("rows", [])

        if not standings:
            return "❌ داده‌ای برای جدول لیگ در API سایت Sofascore یافت نشد."
        
        table_text = f"📊 **جدول لیگ برتر خلیج فارس (منبع: Sofascore)**\n\n"
        table_text += "`"
        table_text += "R | تیم         | B | W | D | L | Pts\n"
        table_text += "-------------------------------------\n"

        for team_info in standings:
            rank = team_info.get("position", "-")
            name_fa = team_info.get("team", {}).get("name", "تیم نامشخص")
            
            # برخی نام‌ها در این API نیاز به ترجمه یا اصلاح دارند
            team_name_map = {
                "Esteghlal Khuzestan": "استقلال خوزستان",
                "Persepolis": "پرسپولیس",
                "Esteghlal": "استقلال",
                "Tractor": "تراکتور",
                "Zob Ahan": "ذوب آهن",
                "Malavan": "ملوان",
                "Gol Gohar": "گل گهر",
                "Shams Azar Qazvin": "شمس آذر قزوین",
                "Mes Rafsanjan": "مس رفسنجان"
            }
            name_fa = team_name_map.get(name_fa, name_fa)

            played = team_info.get("matches", "-")
            wins = team_info.get("wins", "-")
            draws = team_info.get("draws", "-")
            losses = team_info.get("losses", "-")
            points = team_info.get("points", "-")

            table_text += f"{str(rank):<2}| {name_fa:<12}| {str(played):<2}| {str(wins):<2}| {str(draws):<2}| {str(losses):<2}| {str(points):<3}\n"
        
        table_text += "`"
        return table_text
    except Exception as e:
        print(f"Error getting data from Sofascore API: {e}")
        return f"⚠️ خطایی در دریافت اطلاعات از API سایت Sofascore رخ داد:\n`{e}`"

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
    table = get_table_from_sofascore()
    send_or_edit_telegram_message(table)
