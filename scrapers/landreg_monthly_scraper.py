"""
Land Registry Monthly Statistics Scraper
Fetches official monthly transaction consideration statistics from data.gov.hk
"""
import os
import json
import urllib.request
import datetime

def scrape_landreg_monthly():
    url = "https://www.landreg.gov.hk/datagovhk/consideration_2025.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode("utf-8-sig")
        data = json.loads(content)

    output = {
        "metadata": {
            "title": "土地註冊處 - 每月送交註冊的住宅樓宇買賣合約數目(按金額分類)",
            "source": "香港特別行政區政府 土地註冊處 (data.gov.hk hk-lr-data5-landreg)",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "records_count": len(data)
        },
        "data": data
    }
    return output

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    stats = scrape_landreg_monthly()
    with open("data/landreg_monthly_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"Saved Land Registry stats successfully to data/landreg_monthly_stats.json")
