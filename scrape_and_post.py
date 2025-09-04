import os
import requests

# خواندن اطلاعات از سکرت‌های گیت‌هاب
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

def get_cat_fact():
    """یک دانستنی تصادفی درباره گربه‌ها از یک API عمومی دریافت می‌کند."""
    url = "https://catfact.ninja/fact"
    print(f"Connecting to {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # بررسی خطا در درخواست
        data = response.json()
        
        fact = data.get("fact")
        if fact:
            return f"✅ تست API موفق بود!\n\n🐱 دانستنی گربه:\n{fact}"
        else:
            return "❌ تست API انجام شد، اما داده‌ای دریافت نشد."

    except Exception as e:
        print(f"An error occurred: {e}")
        return f"❌ تست API ناموفق بود. خطایی در اتصال به API رخ داد:\n`{e}`"

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
        print("Test message sent successfully to Telegram!")
    else:
        print(f"Failed to send message to Telegram: {response.text}")

if __name__ == "__main__":
    test_message = get_cat_fact()
    send_to_telegram(test_message)
