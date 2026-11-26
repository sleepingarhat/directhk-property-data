"""
Centaline CCI Constituent Estates Master Scraper with Validation & Fail-safe
Fetches official 150+ constituent estates metadata from Centaline Open Data on data.gov.hk
"""
import os
import json
import csv
import io
import urllib.request
import urllib.error
import datetime

def validate_and_clean_estate(row):
    name_tc = (row.get("c_estate") or "").strip()
    name_en = (row.get("e_estate") or "").strip()
    addr_tc = (row.get("pc_addr") or "").strip()
    addr_en = (row.get("pe_addr") or "").strip()
    region = (row.get("scp_mkte") or "").strip()

    if not name_tc:
        return None

    def clean_int(val):
        if not val:
            return None
        val_clean = str(val).strip()
        try:
            return int(val_clean)
        except ValueError:
            return val_clean

    return {
        "estate_name_tc": name_tc,
        "estate_name_en": name_en,
        "address_tc": addr_tc,
        "address_en": addr_en,
        "district_region": region,
        "intake_year_from": str(clean_int(row.get("min_opdate")) or ""),
        "intake_year_to": str(clean_int(row.get("max_opdate")) or ""),
        "total_blocks": str(clean_int(row.get("blgcount")) or ""),
        "developer": (row.get("pc_dev") or "").strip(),
        "centanet_url": (row.get("url") or "").strip()
    }

def scrape_centaline_estates():
    data_path = "data/centaline_estates_master.json"
    existing_data = None
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            pass

    url = "http://hk.centanet.com/opendata/CCI%20Estate%20for%20Opendata.csv"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8-sig", errors="ignore")

        reader = csv.DictReader(io.StringIO(content))
        estates = []
        seen = set()
        duplicates_count = 0

        for row in reader:
            cleaned = validate_and_clean_estate(row)
            if not cleaned:
                continue
            key = (cleaned["estate_name_tc"], cleaned["address_tc"])
            if key in seen:
                duplicates_count += 1
                continue
            seen.add(key)
            estates.append(cleaned)

        if not estates:
            raise ValueError("Parsed 0 estates from Centaline Open Data")

        estates.sort(key=lambda x: (x.get("district_region", ""), x.get("estate_name_tc", "")))

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {
            "metadata": {
                "title": "中原城市領先指數(CCI)成份屋苑官方基礎數據庫",
                "source": "中原地產代理有限公司 (data.gov.hk centaline-centanetod-ccipropertyinfo)",
                "updated_at": now_iso,
                "last_attempt_at": now_iso,
                "validation_status": "passed",
                "total_estates": len(estates),
                "duplicates_filtered": duplicates_count
            },
            "estates": estates
        }

    except Exception as e:
        print(f"[Warning] Centaline scrape failed ({type(e).__name__}: {e}); falling back to existing data.")
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if existing_data:
            existing_data["metadata"]["last_attempt_at"] = now_iso
            existing_data["metadata"]["status"] = "fallback_preserved"
            existing_data["metadata"]["runner_note"] = f"Fetch failed ({type(e).__name__}); preserved existing data."
            return existing_data
        raise

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    master = scrape_centaline_estates()
    with open("data/centaline_estates_master.json", "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    print(f"Saved Centaline master successfully ({master['metadata']['total_estates']} estates)")
