# 香港房地產真實成交與估價採集架構 (Architecture)

## 1. 採集管道設計 (Data Pipelines)
- **土地註冊處官方登記 (Monthly/Weekly)**：透過香港政府資料一線通 (data.gov.hk) 及土地註冊處開放數據，抓取正式成交登記，作為絕對客觀真實的基準（Ground Truth）。
- **各大行一手/二手成交速報 (Daily)**：每日自動抓取美聯、中原、利嘉閣及 28Hse 即日成交，補足土地註冊處 2-4 週滯後期的空窗。
- **銀行估價雷達 (Daily Valuation)**：定時對香港 100 大主流屋苑進行匯豐、中銀、恒生公開估價查詢，計算即時折讓率。

## 2. 數據清洗與防偽機制 (Data Integrity)
- **離群值檢測**：過濾親屬內部轉讓（成交價異常低）、天價成交（特殊複式單位標記）。
- **地址標準化**：將各家寫法（如「太古城金星閣」與「太古城第2期金星閣」）統整為標準房屋代碼。

## 3. 邊緣存儲與前端 API (Cloudflare D1 & Worker)
- GitHub Actions 定時執行 Python 爬蟲。
- 清洗後的結構化數據直接執行 SQL 寫入 Cloudflare D1 或導出 JSON 到 GitHub Releases / Pages。
- 前端 DirectHK 透過 Edge API 零成本、極低延遲讀取最新行情。
