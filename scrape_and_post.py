import os
import requests
from bs4 import BeautifulSoup

# خواندن اطلاعات از سکرت‌های گیت‌هاب
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

def get_table_from_varzesh3():
    """جدول لیگ را از سایت ورزش سه استخراج می‌کند و به صورت متن فرمت‌شده برمی‌گرداند."""
    url = "https://www.varzesh3.com/football/league/6/%D9%84%DB%8C%DA%AF-%D8%A8%D8%B1%D8%AA%D8%B1-%D8%A7%DB%8C%D8%B1%D8%A7%D9%86"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        league_table = soup.find("table", class_="league-standing-table")

        if not league_table:
            return "❌ ساختار جدول در سایت ورزش سه تغییر کرده است."

        table_text = "📊 **آخرین وضعیت جدول لیگ برتر (منبع: ورزش سه)**\n\n"
        table_text += "`"
        table_text += "R | تیم         | B | W | D | L | Pts\n"
        table_text += "-------------------------------------\n"

        rows = league_table.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            rank, team_name, played, wins, draws, losses, points = (
                cols[0].text.strip(), cols[2].text.strip(), cols[3].text.strip(),
                cols[4].text.strip(), cols[5].text.strip(), cols[6].text.strip(),
                cols[9].text.strip()
            )
            table_text += f"{rank:<2}| {team_name:<12}| {played:<2}| {wins:<2}| {draws:<2}| {losses:<2}| {points:<3}\n"
        
        table_text += "`"
        return table_text
    except Exception as e:
        print(f"Error scraping table: {e}")
        return f"⚠️ خطایی در دریافت اطلاعات از سایت ورزش سه رخ داد:\n`{e}`"

def send_to_telegram(message):
    """پیام را به کانال تلگرام ارسال می‌کند."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.text}")

if __name__ == "__main__":
    table = get_table_from_varzesh3()
    send_to_telegram(table)
