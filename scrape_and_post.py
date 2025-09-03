import os
import requests
from datetime import datetime

# خواندن اطلاعات از سکرت‌های گیت‌هاب
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
API_KEY = os.environ.get("THESPORTSDB_API_KEY") # استفاده از سکرت جدید
MESSAGE_ID_FILE = "last_message_id.txt" 

def get_table_from_thesportsdb():
    """جدول لیگ را از سرویس پایدار TheSportsDB دریافت می‌کند."""
    
    # شناسه لیگ برتر ایران در این سرویس 4455 است
    current_year = datetime.now().year
    # فرمت آدرس این سرویس متفاوت است
    url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/lookuptable.php?l=4455&s={current_year}-{current_year + 1}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()

        standings = data.get("table")

        if not standings:
            return "❌ سرویس TheSportsDB داده‌ای برای این فصل برنگرداند."

        table_text = f"📊 **جدول لیگ برتر خلیج فارس - فصل {current_year}**\n\n"
        table_text += "`"
        table_text += "R | تیم         | B | W | D | L | Pts\n"
        table_text += "-------------------------------------\n"

        for team_info in standings:
            rank = team_info.get("intRank", "-")
            # این سرویس نام فارسی را در strTeamAlternate ارائه می‌دهد
            team_name_fa = team_info.get("strTeamAlternate", team_info.get("strTeam", "تیم نامشخص")).strip()
            if not team_name_fa: # اگر نام فارسی خالی بود، از نام اصلی استفاده کن
                 team_name_fa = team_info.get("strTeam", "تیم نامشخص")
                 
            played = team_info.get("intPlayed", "-")
            wins = team_info.get("intWin", "-")
            draws = team_info.get("intDraw", "-")
            losses = team_info.get("intLoss", "-")
            points = team_info.get("intPoints", "-")

            table_text += f"{str(rank):<2}| {team_name_fa:<12}| {str(played):<2}| {str(wins):<2}| {str(draws):<2}| {str(losses):<2}| {str(points):<3}\n"
        
        table_text += "`"
        return table_text
    except Exception as e:
        print(f"Error getting data from TheSportsDB: {e}")
        return f"⚠️ خطایی در ارتباط با سرویس TheSportsDB رخ داد:\n`{e}`"

def send_or_edit_telegram_message(message):
    """پیام را به کانال تلگرام ارسال یا ویرایش می‌کند."""
    last_message_id = None
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, "r") as f:
            content = f.read().strip()
            if content.isdigit():
                last_message_id = int(content)

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
    table = get_table_from_thesportsdb()
    send_or_edit_telegram_message(table)
