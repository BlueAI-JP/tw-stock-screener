# 台股市值前100大篩選器
- 重新抓取/建置：`python3 scripts/build.py`（產生 `public/data.json` 與 `public/index.html`）
- 資料來源：TWSE OpenAPI `exchangeReport/STOCK_DAY_ALL`（收盤）+ `opendata/t187ap03_L`（已發行股數）→ 市值 = 收盤×股數，取前100（僅上市普通股，不含ETF/上櫃）；Yahoo Finance chart API (`XXXX.TW`) 取近一個月日收盤，計算當日與5交易日累積漲跌幅。免金鑰。
- 篩選：|當日%|>5、|5日%|>10。休市時顯示最近交易日收盤。
- 部署：GitHub Pages（gh-pages 分支 = public/ 內容）。每日更新：`./deploy.sh`（重新抓資料 + commit + push main + 推送 gh-pages）。需先 `gh auth login` 並 `gh auth setup-git`。
