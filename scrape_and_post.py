import os
import requests

# خواندن اطلاعات از سکرت‌های گیت‌هاب
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
API_KEY = os.environ.get("RAPIDAPI_KEY")
API_HOST = os.environ.get("RAPIDAPI_HOST")
MESSAGE_ID_FILE = "last_message_id.txt" 

def get_table_from_rapidapi():
    """جدول لیگ را از سرویس free-api-live-football-data در RapidAPI دریافت می‌کند."""
    # شناسه لیگ برتر ایران در این سرویس 188 است
    url = "https://free-api-live-football-data.p.rapidapi.com/leagues-standings"
    querystring = {"league_id":"188"}
    
    headers = {
        "x-rapidapi-host": API_HOST,
        "x-rapidapi-key": API_KEY
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=20)
        response.raise_for_status()
        data = response.json()

        if not data.get("success") or not data.get("data", {}).get("standings"):
            return "❌ داده‌ای برای جدول لیگ در این API یافت نشد."

        standings = data["data"]["standings"]
        league_name = data["data"]["league_name"]

        table_text = f"📊 **{league_name} (منبع: RapidAPI)**\n\n"
        table_text += "`"
        table_text += "R | تیم         | B | W | D | L | Pts\n"
        table_text += "-------------------------------------\n"

        for team_info in standings:
            rank = team_info.get("rank", "-")
            name = team_info.get("team_name", "تیم نامشخص")
            played = team_info.get("all_played", "-")
            wins = team_info.get("all_win", "-")
            draws = team_info.get("all_draw", "-")
            losses = team_info.get("all_lose", "-")
            points = team_info.get("points", "-")

            table_text += f"{str(rank):<2}| {name:<12}| {str(played):<2}| {str(wins):<2}| {str(draws):<2}| {str(losses):<2}| {str(points):<3}\n"
        
        table_text += "`"
        return table_text
    except Exception as e:
        print(f"Error getting data from RapidAPI: {e}")
        return f"⚠️ خطایی در ارتباط با RapidAPI رخ داد:\n`{e}`"

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
    table = get_table_from_rapidapi()
    send_or_edit_telegram_message(table)
