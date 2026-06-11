from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
import json, os, datetime as dt, requests
import pandas as pd
import yfinance as yf

APP_DIR = Path(__file__).resolve().parent
DB = APP_DIR / "portfolio.json"
FINMIND = "https://api.finmindtrade.com/api/v4/data"
TOKEN = os.getenv("FINMIND_TOKEN", "")

app = FastAPI(title="BullStreet Portfolio API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Holding(BaseModel):
    symbol: str = Field(..., examples=["2313", "MU"])
    name: str = ""
    market: str = Field("TW", examples=["TW", "US"])
    shares: float
    avg_cost: float
    note: str = ""

CONCEPTS = {
    "2313": ["PCB", "AI Server", "Apple Supply Chain", "CCL"],
    "2382": ["AI Server", "ODM", "NVIDIA GB200"],
    "3231": ["AI Server", "PCB"],
    "2330": ["Semiconductor", "AI Chip", "Foundry"],
    "MU": ["DRAM", "HBM", "AI Memory", "Semiconductor"],
    "NVDA": ["AI GPU", "Datacenter", "Semiconductor"],
    "AMD": ["AI Accelerator", "CPU", "Semiconductor"],
}
RELATED = {
    "PCB": ["2313", "2368", "3037", "3189", "4958"],
    "AI Server": ["2382", "3231", "6669", "2356", "3017"],
    "DRAM": ["MU", "2408", "2337", "2344"],
    "Semiconductor": ["2330", "NVDA", "AMD", "ASML", "MU"],
}

def load_db():
    if not DB.exists():
        DB.write_text("[]", encoding="utf-8")
    return json.loads(DB.read_text(encoding="utf-8"))

def save_db(data):
    DB.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def finmind(dataset, data_id, start_date="2024-01-01"):
    params = {"dataset": dataset, "data_id": data_id, "start_date": start_date}
    if TOKEN: params["token"] = TOKEN
    r = requests.get(FINMIND, params=params, timeout=12)
    r.raise_for_status()
    payload = r.json()
    if payload.get("status") not in [200, "200"]:
        return []
    return payload.get("data", [])

def taiwan_quote(symbol):
    start = (dt.date.today() - dt.timedelta(days=120)).isoformat()
    rows = finmind("TaiwanStockPrice", symbol, start)
    if not rows: return None
    df = pd.DataFrame(rows)
    last = df.iloc[-1]
    close = float(last["close"])
    ma20 = float(df.tail(20)["close"].mean()) if len(df) >= 20 else close
    ma60 = float(df.tail(60)["close"].mean()) if len(df) >= 60 else close
    ret20 = (close / float(df.iloc[-21]["close"]) - 1) * 100 if len(df) > 21 else 0
    return {"price": close, "date": str(last["date"]), "ma20": round(ma20,2), "ma60": round(ma60,2), "ret20": round(ret20,2), "volume": int(last.get("Trading_Volume",0))}

def us_quote(symbol):
    t = yf.Ticker(symbol)
    hist = t.history(period="6mo")
    if hist.empty: return None
    close = float(hist["Close"].iloc[-1])
    return {"price": round(close,2), "date": str(hist.index[-1].date()), "ma20": round(float(hist["Close"].tail(20).mean()),2), "ma60": round(float(hist["Close"].tail(60).mean()),2), "ret20": round((close/float(hist["Close"].iloc[-21])-1)*100,2) if len(hist)>21 else 0, "volume": int(hist["Volume"].iloc[-1])}

def analyze_signal(q):
    score = 50
    if q["price"] > q["ma20"]: score += 12
    if q["ma20"] > q["ma60"]: score += 12
    if q["ret20"] > 8: score += 8
    if q["ret20"] < -8: score -= 8
    score = max(0, min(100, score))
    if score >= 75: label = "偏多：多頭排列或短線強勢"
    elif score >= 55: label = "中性偏多：可觀察量能與大盤"
    elif score >= 40: label = "中性：等突破或回測支撐"
    else: label = "偏弱：避免追高，等止跌"
    return score, label

@app.get("/api/portfolio")
def get_portfolio():
    return load_db()

@app.post("/api/portfolio")
def add_holding(h: Holding):
    data = load_db()
    data.append(h.model_dump())
    save_db(data)
    return {"ok": True, "holding": h}

@app.delete("/api/portfolio/{idx}")
def delete_holding(idx: int):
    data = load_db()
    if idx < 0 or idx >= len(data): raise HTTPException(404, "holding not found")
    removed = data.pop(idx)
    save_db(data)
    return {"ok": True, "removed": removed}

@app.get("/api/analyze/{symbol}")
def analyze(symbol: str, market: str = "TW"):
    symbol = symbol.upper().strip()
    market = market.upper()
    quote = taiwan_quote(symbol) if market == "TW" else us_quote(symbol)
    if quote is None: raise HTTPException(404, "No quote data. Check symbol/API token/rate limit.")
    score, label = analyze_signal(quote)
    concepts = CONCEPTS.get(symbol, [])
    related = sorted(set(sum([RELATED.get(c, []) for c in concepts], [])))[:12]
    return {
        "symbol": symbol, "market": market, "quote": quote,
        "technical_score": score, "technical_view": label,
        "concepts": concepts, "related_stocks": related,
        "macro_links": ["NASDAQ / SOX 影響半導體與 AI 概念", "美元與美債殖利率影響成長股估值", "台股大盤若跌破月線，個股勝率下降"],
        "todo_data": ["籌碼：三大法人/融資融券", "營收：月營收 YoY/MoM", "財報：EPS/毛利率/營益率"]
    }

@app.get("/api/market")
def market():
    result = {}
    for sym in ["^IXIC", "^SOX", "^GSPC", "^TWII"]:
        try: result[sym] = us_quote(sym)
        except Exception: result[sym] = None
    return result
