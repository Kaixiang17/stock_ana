# BullStreet Portfolio 🐂

Wall Street 科技感的持股分析系統：持股新增、概念股、台股/美股影響、技術面、大盤雷達，手機可瀏覽。

## 功能
- 新增/刪除持股，GitHub Pages 靜態模式會存在瀏覽器 localStorage
- FastAPI 後端可抓台股 FinMind、美股 yfinance
- 個股分析：價格、MA20、MA60、20 日強弱、相關概念股
- 大盤雷達：NASDAQ、SOX、S&P500、台股加權
- RWD 手機版

## API 來源建議
- 台股：FinMind，資料集涵蓋台股日成交、月營收、財報、持股、三大法人等。
- 台股官方：TWSE / MOPS / data.gov.tw 可查營收、財報與本益比等資料。
- 美股：Alpha Vantage 或 yfinance。正式產品建議用 Alpha Vantage / Polygon / Finnhub 等有明確授權的 API。

## 本機啟動
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

再開啟 `frontend/index.html`。

## FinMind Token
```bash
export FINMIND_TOKEN="你的 token"
```
沒有 token 也可試用部分資料，但容易遇到限制。

## GitHub Pages
把 `frontend/` 裡面三個檔案放到 repo root，或設定 Pages 指到 `/frontend`。靜態模式可以新增持股，但即時 API 分析需要另外部署後端。

## 後端部署
建議 Render / Railway / Fly.io。部署後把 `frontend/app.js` 的 API 改成你的後端網址：
```js
const API = 'https://your-api.onrender.com';
```

## 下一版可以加
- 月營收 YoY/MoM
- 三大法人買賣超
- 融資融券
- EPS、毛利率、營益率
- AI 新聞摘要與事件分數
- 使用者登入與雲端同步
