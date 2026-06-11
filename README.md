# BullStreet AI

Wall Street 科技感投資儀表板：登入後可管理持股、AI 分析、LINE 推播、台股/美股預警、權證與 ETF 分析。手機可瀏覽。

## 功能

- 登入 / 註冊
- 我的持股：新增台股、美股、ETF、權證
- AI 分析：概念股、基本面、技術面、籌碼面、大盤影響
- LINE 推播：保留 LINE Messaging API 設定
- 台股預警 / 美股預警 / ETF / 權證分析
- RWD 手機版 UI

## 本機啟動

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend: http://localhost:8000
API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

Demo 帳號：

```txt
demo@bullstreet.ai / demo123
```

## GitHub 上傳

```bash
git init
git add .
git commit -m "Initial BullStreet AI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/bullstreet-ai.git
git push -u origin main
```

## 部署建議

### Frontend

可部署到：

- GitHub Pages
- Vercel
- Netlify

若後端部署到 Render，請在 frontend 設定：

```env
VITE_API_URL=https://你的-render-backend.onrender.com
```

### Backend

可部署到：

- Render
- Railway
- Fly.io

環境變數：

```env
JWT_SECRET=請換成很長的隨機字串
DATABASE_URL=sqlite:///./bullstreet.db
LINE_CHANNEL_ACCESS_TOKEN=你的_LINE_TOKEN
LINE_USER_ID=你的_LINE_USER_ID
```

## API 串接方向

目前專案先做成可跑的完整架構，報價用 mock fallback，之後可以接：

- 台股：FinMind、證交所 OpenAPI、Goodinfo 手動匯入
- 美股：yfinance、Alpha Vantage、Finnhub
- 總經：FRED、Alpha Vantage
- LINE：Messaging API 或 Make.com webhook

## 專案結構

```txt
bullstreet_ai/
├── frontend/       React + Vite
├── backend/        FastAPI + SQLite
└── README.md
```
