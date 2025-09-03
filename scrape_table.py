# scrape_table.py
import requests
from bs4 import BeautifulSoup
import json

URL = "https://iranleague.ir/fa/League/LeagueTable/16"  
# عدد 16 مربوط به لیگ برتر خلیج فارس (ممکنه هر فصل ID تغییر کنه)

headers = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_table():
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # جدول اصلی در iranleague.ir در تگ <table> با کلاس "table" هست
    rows = soup.select("table tbody tr")

    table = []
    for tr in rows:
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        # انتظار داریم ترتیب ستون‌ها این باشه:
        # رده | تیم | بازی | برد | مساوی | باخت | زده | خورده | تفاضل | امتیاز
        if len(cols) >= 10:
            team = cols[1]
            table.append({
                "position": int(cols[0]),
                "team": team,
                "played": int(cols[2]),
                "win": int(cols[3]),
                "draw": int(cols[4]),
                "loss": int(cols[5]),
                "goalsFor": int(cols[6]),
                "goalsAgainst": int(cols[7]),
                "goalDifference": int(cols[8]),
                "points": int(cols[9])
            })

    return {
        "league": "Persian Gulf Pro League",
        "table": table
    }

if __name__ == "__main__":
    data = scrape_table()
    with open("table.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ table.json ساخته شد و شامل", len(data["table"]), "تیم است.")
