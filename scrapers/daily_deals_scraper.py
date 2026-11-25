"""
Daily Deals Scraper Example
爬取每日二手成交並對齊標準屋苑字段
"""
import json
import datetime

def scrape_daily_transactions():
    today = datetime.date.today().isoformat()
    print(f"[{today}] Fetching real estate transactions from verified public feeds...")
    
    # 示例標準數據結構
    sample_records = [
        {
            "estate_name": "太古城",
            "district": "東區",
            "block": "海天閣",
            "floor": "中層",
            "flat": "B",
            "saleable_area": 759,
            "trans_price_hkd": 12800000,
            "unit_price_sqft": 16864,
            "trans_date": today,
            "source": "美聯/中原成交登記",
            "bank_valuation_avg": 13100000,
            "premium_discount_pct": -2.29
        }
    ]
    return sample_records

if __name__ == "__main__":
    records = scrape_daily_transactions()
    with open("data/latest_transactions.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print("Done! Exported to data/latest_transactions.json")
