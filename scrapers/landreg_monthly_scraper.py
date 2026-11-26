"""
Land Registry Monthly Statistics Scraper with Validation & Fail-safe
Fetches official monthly transaction consideration statistics from data.gov.hk
"""
import os
import json
import urllib.request
import urllib.error
import datetime

def scrape_landreg_monthly():
    data_path = "data/landreg_monthly_stats.json"
    existing_data = None
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except Exception:
            pass

    url = "https://www.landreg.gov.hk/datagovhk/consideration_2025.json"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8-sig")
            data = json.loads(content)

        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Invalid format: expected non-empty list of consideration statistics")

        seen_brackets = set()
        valid_records = []
        duplicates_count = 0

        for row in data:
            bracket = (row.get("Range of Consideration ($ million)") or "").strip()
            if not bracket:
                continue
            if bracket in seen_brackets:
                duplicates_count += 1
                continue
            seen_brackets.add(bracket)
            valid_records.append(row)

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {
            "metadata": {
                "title": "土地註冊處 - 每月送交註冊的住宅樓宇買賣合約數目(按金額分類)",
                "source": "香港特別行政區政府 土地註冊處 (data.gov.hk hk-lr-data5-landreg)",
                "updated_at": now_iso,
                "last_attempt_at": now_iso,
                "validation_status": "passed",
                "records_count": len(valid_records),
                "duplicates_filtered": duplicates_count
            },
            "data": valid_records
        }

    except Exception as e:
        print(f"[Warning] Land Registry scrape failed ({type(e).__name__}: {e}); falling back to existing data.")
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if existing_data:
            existing_data["metadata"]["last_attempt_at"] = now_iso
            existing_data["metadata"]["status"] = "fallback_preserved"
            existing_data["metadata"]["runner_note"] = f"Fetch failed ({type(e).__name__}); preserved existing data."
            return existing_data
        raise

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    stats = scrape_landreg_monthly()
    with open("data/landreg_monthly_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"Saved Land Registry stats successfully to data/landreg_monthly_stats.json ({stats['metadata']['records_count']} rows)")
