#!/usr/bin/env python3
"""Fetch TWSE top-100 by market cap and build public/data.json + index.html."""
import json, urllib.request, datetime, concurrent.futures as cf, pathlib, shutil
TZ = datetime.timezone(datetime.timedelta(hours=8))
ROOT = pathlib.Path(__file__).resolve().parent.parent
def get(url):
    r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r, timeout=30))
day = get("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL")
info = {c["公司代號"]: c for c in get("https://openapi.twse.com.tw/v1/opendata/t187ap03_L")}
rows = []
for d in day:
    c = info.get(d["Code"])
    try: close = float(d["ClosingPrice"]); sh = int(c["已發行普通股數或TDR原股發行股數"])
    except Exception: continue
    rows.append({"code": d["Code"], "name": c["公司簡稱"] or d["Name"], "mcap": close * sh})
rows.sort(key=lambda r: -r["mcap"]); top = rows[:100]
def hist(r):
    try:
        j = get(f"https://query1.finance.yahoo.com/v8/finance/chart/{r['code']}.TW?range=1mo&interval=1d")["chart"]["result"][0]
        pts = [(t, c) for t, c in zip(j["timestamp"], j["indicators"]["quote"][0]["close"]) if c is not None]
        cl = [c for _, c in pts]
        r["close"] = round(cl[-1], 2)
        r["date"] = datetime.datetime.fromtimestamp(pts[-1][0], TZ).strftime("%Y-%m-%d")
        r["chg1"] = round((cl[-1] / cl[-2] - 1) * 100, 2)
        r["chg5"] = round((cl[-1] / cl[-6] - 1) * 100, 2)
    except Exception as e:
        r["error"] = str(e)
    r["mcap_yi"] = round(r.pop("mcap") / 1e8)
    m = []
    if abs(r.get("chg1", 0)) > 5: m.append("當日±5%")
    if abs(r.get("chg5", 0)) > 10: m.append("5日±10%")
    r["match"] = m
    return r
with cf.ThreadPoolExecutor(10) as ex: top = list(ex.map(hist, top))
out = {"updated": datetime.datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S (台北時間 UTC+8)"),
       "trade_date": max((r.get("date", "") for r in top)), "stocks": top}
(ROOT / "public/data.json").write_text(json.dumps(out, ensure_ascii=False))
shutil.copy(ROOT / "src/index.html", ROOT / "public/index.html")
print(len(top), "stocks;", sum("當日±5%" in r["match"] for r in top), "day>5%;",
      sum("5日±10%" in r["match"] for r in top), "5d>10%;", sum("error" in r for r in top), "errors")
