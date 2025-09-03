import os
import requests

# خواندن اطلاعات از سکرت‌های گیت‌هاب
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
MESSAGE_ID_FILE = "last_message_id.txt" 

def get_table_from_api():
    """جدول لیگ را مستقیماً از API داخلی سایت ورزش سه دریافت می‌کند."""
    # این لینک، منبع اصلی داده‌های جدول در خود سایت است و بسیار پایدارتر از HTML است
    url = "https://service.varzesh3.com/v2/leagues/6/standings"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        # استخراج لیست تیم‌ها از پاسخ JSON
        standings = data.get("data", {}).get("standings")

        if not standings:
            return "❌ API سایت ورزش سه داده‌ای برنگرداند یا ساختار آن تغییر کرده است."

        table_text = "📊 **آخرین وضعیت جدول لیگ برتر (منبع: Varzesh3 API)**\n\n"
        table_text += "`"
        table_text += "R | تیم         | B | W | D | L | Pts\n"
        table_text += "-------------------------------------\n"

        # خواندن اطلاعات هر تیم از داده‌های API
        for team in standings:
            rank = team.get("rank", "-")
            team_name = team.get("team", {}).get("name_fa", "تیم نامشخص")
            played = team.get("games_played", "-")
            wins = team.get("wins", "-")
            draws = team.get("draws", "-")
            losses = team.get("losses", "-")
            points = team.get("points", "-")

            table_text += f"{str(rank):<2}| {team_name:<12}| {str(played):<2}| {str(wins):<2}| {str(draws):<2}| {str(losses):<2}| {str(points):<3}\n"
        
        table_text += "`"
        return table_text
    except Exception as e:
        print(f"Error getting data from API: {e}")
        return f"⚠️ خطایی در دریافت اطلاعات از API ورزش سه رخ داد:\n`{e}`"

def send_or_edit_telegram_message(message):
    """
    پیام را به کانال تلگرام ارسال می‌کند. اگر پیامی از قبل ارسال شده باشد،
    آن را ویرایش می‌کند تا از شلوغ شدن کانال جلوگیری شود.
    """
    last_message_id = None
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, "r") as f:
            content = f.read().strip()
            if content.isdigit():
                last_message_id = int(content)

    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
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
        with open(MESSAGE_ID_FILE, "w") as f:
            f.write(str(new_message_id))
        print(f"Message sent/edited successfully! Message ID: {new_message_id}")
    else:
        print(f"Failed to send/edit message: {response.text}")

if __name__ == "__main__":
    table = get_table_from_api()
    send_or_edit_telegram_message(table)
