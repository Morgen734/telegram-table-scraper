import os
import requests
import json
import re
from bs4 import BeautifulSoup

# خواندن اطلاعات از سکرت‌های گیت‌هاب
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
MESSAGE_ID_FILE = "last_message_id.txt" 

def get_table_from_varzesh3_json():
    """جدول لیگ را با استخراج داده‌های JSON پنهان در سورس کد سایت ورزش سه دریافت می‌کند."""
    url = "https://www.varzesh3.com/football/league/6/%D9%84%DB%8C%DA%AF-%D8%A8%D8%B1%D8%AA%D8%B1-%D8%A7%DB%8C%D8%B1%D8%A7%D9%86"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        
        # پیدا کردن تمام تگ‌های اسکریپت
        scripts = soup.find_all("script")
        
        standings_data = None
        for script in scripts:
            # اسکریپتی را پیدا می‌کنیم که حاوی داده‌های جدول (standings) است
            if script.string and '"standings":' in script.string:
                # با استفاده از عبارت منظم، آبجکت JSON را از داخل متن اسکریپت استخراج می‌کنیم
                match = re.search(r'("standings":\{.*?"teams":\[.*?\]\ K\},)', script.string)
                if match:
                    # اصلاح جزئی برای تبدیل کردن متن به یک JSON معتبر
                    json_text = "{" + match.group(1).replace("},}", "}}") + "}"
                    try:
                        data = json.loads(json_text)
                        standings_data = data['standings']['teams']
                        break
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        continue
        
        if not standings_data:
            return "❌ داده‌های جدول در سورس کد سایت پیدا نشد. (نیاز به آپدیت)"

        table_text = "📊 **جدول لیگ برتر (منبع: ورزش سه)**\n\n"
        table_text += "`"
        table_text += "R | تیم         | B | W | D | L | Pts\n"
        table_text += "-------------------------------------\n"

        for team in standings_data:
            rank = team.get("rank", "-")
            name = team.get("name", "تیم نامشخص")
            played = team.get("played", "-")
            wins = team.get("wins", "-")
            draws = team.get("draws", "-")
            losses = team.get("losses", "-")
            points = team.get("points", "-")

            table_text += f"{str(rank):<2}| {name:<12}| {str(played):<2}| {str(wins):<2}| {str(draws):<2}| {str(losses):<2}| {str(points):<3}\n"
        
        table_text += "`"
        return table_text
    except Exception as e:
        print(f"Error scraping Varzesh3 JSON: {e}")
        return f"⚠️ خطایی در خواندن اطلاعات از ورزش سه رخ داد:\n`{e}`"

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
    table = get_table_from_varzesh3_json()
    send_or_edit_telegram_message(table)
