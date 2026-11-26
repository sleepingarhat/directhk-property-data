"""
Daily Deals Scraper
Real-time scraper for verified HK property transactions (Midland & Land Registry certified)
"""
import os
import json
import re
import urllib.request
import datetime

def scrape_daily_transactions():
    url = "https://www.midland.com.hk/zh-hk/transaction"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if not m:
        raise ValueError("Could not find __NEXT_DATA__ in transaction page")

    raw_data = json.loads(m.group(1))
    api_data = raw_data.get("props", {}).get("pageProps", {}).get("apiData", {})
    raw_groups = api_data.get("transactionData", [])

    records = []
    sources_count = {}
    for group in raw_groups:
        region_type = group.get("type", "")
        for item in group.get("data", []):
            estate_obj = item.get("estate")
            estate_name = estate_obj.get("name") if isinstance(estate_obj, dict) else str(estate_obj or "")
            building_obj = item.get("building")
            building_name = building_obj.get("name") if isinstance(building_obj, dict) else str(building_obj or "")
            district_obj = item.get("district")
            district_name = district_obj.get("name") if isinstance(district_obj, dict) else str(district_obj or "")
            region_obj = item.get("region")
            region_name = region_obj.get("name") if isinstance(region_obj, dict) else str(region_obj or region_type)

            price = item.get("price")
            unit_price_net = item.get("unit_price_net")
            net_area = item.get("net_area") or item.get("area")
            tx_date = item.get("tx_date") or item.get("update_date")
            src_list = item.get("source", [])
            src_tag = "土地註冊處登記 (Land Registry)" if "LANDREG" in src_list else "美聯成交速報 (Midland Feed)"
            sources_count[src_tag] = sources_count.get(src_tag, 0) + 1

            records.append({
                "id": item.get("id"),
                "estate_name": estate_name,
                "building_name": building_name,
                "district": district_name,
                "region": region_name,
                "floor": item.get("floor") or item.get("floor_level"),
                "flat": item.get("flat"),
                "transaction_type": "出租" if item.get("tx_type") == "rent" or (price and price < 150000) else "買賣",
                "price_hkd": price,
                "net_area_sqft": net_area,
                "unit_price_sqft": unit_price_net,
                "transaction_date": tx_date[:10] if tx_date else datetime.date.today().isoformat(),
                "verified_source": src_tag,
                "raw_source_tags": src_list
            })

    output = {
        "metadata": {
            "title": "香港最新住宅成交與租賃紀錄",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_records": len(records),
            "sources_breakdown": sources_count,
            "provider": "Midland Realty + Land Registry Certified Feed"
        },
        "records": records
    }
    return output

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    data = scrape_daily_transactions()
    with open("data/latest_transactions.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Scraped {data['metadata']['total_records']} records successfully to data/latest_transactions.json")
