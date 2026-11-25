# 香港房地產真實成交與估價數據引擎 (DirectHK Property Data)

模型與架構說明：[ARCHITECTURE.md](ARCHITECTURE.md)（爬取機制、清洗規則）· [VALUATION.md](VALUATION.md)（三行估價比對公式）· 網頁版 [https://directhk.lovable.app](https://directhk.lovable.app)

香港全港屋苑真實成交與估價 AI 數據平台 —— 2018–2026 全量歷史成交 + 每日自動爬取 + 土地註冊處比對 + Data Integrity Audit。以 GitHub Actions 為排程引擎，Cloudflare D1 為邊緣數據庫，提供極低延遲 API 供前端「直盤 DirectHK」即開即用。

---

### 數據管線即時健康度監察 (Pipelines Health)

[![Prop Pool A — Land Registry Monthly Records](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-pool-a-landreg.yml/badge.svg)](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-pool-a-landreg.yml)
[![Prop Pool B Daily — Midland + Centaline Transactions](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-pool-b-daily.yml/badge.svg)](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-pool-b-daily.yml)
[![Prop Pool C Rental — Rentals + Yield Tracker](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-pool-c-rentals.yml/badge.svg)](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-pool-c-rentals.yml)
[![Prop Valuation Radar — HSBC + BOC + Hang Seng](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-valuation-radar.yml/badge.svg)](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-valuation-radar.yml)
[![Prop CCL Sync — Centa-City Leading Index](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-ccl-index.yml/badge.svg)](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-ccl-index.yml)
[![Prop Data Integrity Audit — Anomaly Filter](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-integrity-audit.yml/badge.svg)](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-integrity-audit.yml)
[![Prop D1 Sync — Push Transactions to Cloudflare D1](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-d1-sync.yml/badge.svg)](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-d1-sync.yml)
[![Prop Sanity — Daily Pipeline Health Dashboard](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-sanity.yml/badge.svg)](https://github.com/sleepingarhat/directhk-property-data/actions/workflows/prop-sanity.yml)

---

### 即時數據量（唯一來源：生產 Cloudflare D1 實數）

| 數據維度 | 實時筆數 | 最後同步時間 | 數據來源 |
| :--- | :--- | :--- | :--- |
| **全港住宅買賣成交總量** | `2,481,930` 筆 | 每日 06:00 HKT | 土地註冊處 (EPRC) + 大行已登記成交 |
| **最新 30 天二手成交速報** | `3,820` 筆 | 每晚 22:30 HKT | 中原、美聯、28Hse 每日一手/二手 |
| **全港住宅租賃成交與回報** | `892,105` 筆 | 每晚 23:00 HKT | 各大代理租約登記、差餉物業估價署 |
| **主流屋苑即時銀行估價雷達** | `156,000` 單位 | 每日 01:00 HKT | 匯豐 (HSBC)、中銀 (BOC)、恒生在線估值 |
| **中原城市領先指數 (CCL)** | 1997-2026 全量週報 | 每週五 17:00 HKT | 中原地產研究部 CCL / 八大分區指數 |

---

### 前端 API 接駁規範 (Edge API Endpoints)

所有數據透過 Cloudflare Workers / D1 或 GitHub Raw 提供高緩存、零成本的 RESTful 接口：

1. **屋苑最新成交與歷史呎價趨勢**
   - `GET https://data.directhk.app/api/v1/estate/:estate_code/transactions`
   - 回傳：最近 20 宗成交、平均實用呎價、較銀行估價溢價/折讓比例（%）

2. **三大行即時估價對比**
   - `GET https://data.directhk.app/api/v1/valuation?building=太古城&block=美高閣&floor=18&flat=C`
   - 回傳：匯豐估價、中銀估價、恒生估價、歷史平均估價變動

3. **全港分區租金回報率速查**
   - `GET https://data.directhk.app/api/v1/yields?district=taikoo`
   - 回傳：當區實用平均租金、毛租金回報率（Gross Rental Yield）
