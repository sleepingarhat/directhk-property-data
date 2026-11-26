"""
Centaline CCI Constituent Estates Master Scraper
Fetches official 150+ constituent estates metadata from Centaline Open Data on data.gov.hk
"""
import os
import json
import csv
import io
import urllib.request
import datetime

def scrape_centaline_estates():
    url = "http://hk.centanet.com/opendata/CCI%20Estate%20for%20Opendata.csv"
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        content = resp.read().decode("utf-8-sig", errors="ignore")
    
    reader = csv.DictReader(io.StringIO(content))
    estates = []
    for row in reader:
        estates.append({
            "estate_name_tc": row.get("c_estate"),
            "estate_name_en": row.get("e_estate"),
            "address_tc": row.get("pc_addr"),
            "address_en": row.get("pe_addr"),
            "district_region": row.get("scp_mkte"),
            "intake_year_from": row.get("min_opdate"),
            "intake_year_to": row.get("max_opdate"),
            "total_blocks": row.get("blgcount"),
            "developer": row.get("pc_dev"),
            "centanet_url": row.get("url")
        })

    output = {
        "metadata": {
            "title": "中原城市領先指數(CCI)成份屋苑官方基礎數據庫",
            "source": "中原地產代理有限公司 (data.gov.hk centaline-centanetod-ccipropertyinfo)",
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_estates": len(estates)
        },
        "estates": estates
    }
    return output

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    estates_data = scrape_centaline_estates()
    with open("data/centaline_estates_master.json", "w", encoding="utf-8") as f:
        json.dump(estates_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {estates_data['metadata']['total_estates']} Centaline estates to data/centaline_estates_master.json")
