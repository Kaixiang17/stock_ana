from datetime import datetime, timedelta
import os, random, requests
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

SECRET=os.getenv('JWT_SECRET','dev-secret-change-me')
DATABASE_URL=os.getenv('DATABASE_URL','sqlite:///./bullstreet.db')
LINE_TOKEN=os.getenv('LINE_CHANNEL_ACCESS_TOKEN','')
LINE_USER_ID=os.getenv('LINE_USER_ID','')
engine=create_engine(DATABASE_URL,connect_args={'check_same_thread':False} if DATABASE_URL.startswith('sqlite') else {})
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)
Base=declarative_base(); pwd=CryptContext(schemes=['bcrypt'],deprecated='auto'); oauth2=OAuth2PasswordBearer(tokenUrl='auth/login')
app=FastAPI(title='BullStreet AI API')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
class User(Base): __tablename__='users'; id=Column(Integer,primary_key=True); email=Column(String,unique=True); password_hash=Column(String)
class Holding(Base): __tablename__='holdings'; id=Column(Integer,primary_key=True); user_id=Column(Integer); symbol=Column(String); name=Column(String); market=Column(String); shares=Column(Float); avg_price=Column(Float); created_at=Column(DateTime,default=datetime.utcnow)
class Alert(Base): __tablename__='alerts'; id=Column(Integer,primary_key=True); user_id=Column(Integer); symbol=Column(String); condition=Column(String); target=Column(Float); channel=Column(String,default='line'); enabled=Column(Integer,default=1)
Base.metadata.create_all(bind=engine)
class AuthIn(BaseModel): email:str; password:str
class HoldingIn(BaseModel): symbol:str; name:str=''; market:str='TW'; shares:float; avg_price:float
class AlertIn(BaseModel): symbol:str; condition:str; target:float; channel:str='line'
def db():
    s=SessionLocal();
    try: yield s
    finally: s.close()
def tok(user): return jwt.encode({'sub':str(user.id),'exp':datetime.utcnow()+timedelta(days=30)},SECRET,algorithm='HS256')
def me(t=Depends(oauth2),s:Session=Depends(db)):
    try: uid=int(jwt.decode(t,SECRET,algorithms=['HS256'])['sub'])
    except JWTError: raise HTTPException(401,'invalid token')
    u=s.get(User,uid)
    if not u: raise HTTPException(401,'user not found')
    return u
def seed(s):
    u=s.query(User).filter_by(email='demo@bullstreet.ai').first()
    if not u:
        u=User(email='demo@bullstreet.ai',password_hash=pwd.hash('demo123'));s.add(u);s.commit();s.refresh(u)
        s.add_all([Holding(user_id=u.id,symbol='2330',name='台積電',market='TW',shares=20,avg_price=850),Holding(user_id=u.id,symbol='NVDA',name='NVIDIA',market='US',shares=5,avg_price=125),Holding(user_id=u.id,symbol='0050',name='元大台灣50',market='ETF',shares=100,avg_price=160),Holding(user_id=u.id,symbol='061862',name='華通元富63購01',market='WARRANT',shares=15000,avg_price=1.40)])
        s.add(Alert(user_id=u.id,symbol='NASDAQ',condition='price_above',target=26000,channel='line'));s.commit()
with SessionLocal() as s: seed(s)
@app.post('/auth/register')
def register(x:AuthIn,s:Session=Depends(db)):
    if s.query(User).filter_by(email=x.email).first(): raise HTTPException(400,'exists')
    u=User(email=x.email,password_hash=pwd.hash(x.password));s.add(u);s.commit();s.refresh(u);return {'access_token':tok(u)}
@app.post('/auth/login')
def login(x:AuthIn,s:Session=Depends(db)):
    u=s.query(User).filter_by(email=x.email).first()
    if not u or not pwd.verify(x.password,u.password_hash): raise HTTPException(401,'bad credentials')
    return {'access_token':tok(u)}
def quote(symbol,market):
    base={'2330':950,'2313':275,'0050':185,'NVDA':142,'MU':96,'NASDAQ':23800,'061862':1.38}.get(symbol.upper(), random.uniform(50,300))
    return round(base*random.uniform(.985,1.025),2)
@app.get('/dashboard')
def dashboard(u:User=Depends(me),s:Session=Depends(db)):
    hs=s.query(Holding).filter_by(user_id=u.id).all(); rows=[]; total=cost=0
    for h in hs:
        last=quote(h.symbol,h.market); mv=last*h.shares; c=h.avg_price*h.shares; total+=mv; cost+=c
        rows.append({'id':h.id,'symbol':h.symbol,'name':h.name,'market':h.market,'shares':h.shares,'avg_price':h.avg_price,'last_price':last,'market_value':round(mv,2),'pnl':round(mv-c,2),'pnl_pct':round((mv-c)/c*100,2) if c else 0})
    pnl=total-cost
    chart=[{'day':f'D-{9-i}','price':round(100+random.uniform(-4,8)+i*1.7,2)} for i in range(10)]
    return {'summary':{'total_value':round(total,2),'cost':round(cost,2),'pnl':round(pnl,2),'pnl_pct':round(pnl/cost*100,2) if cost else 0},'holdings':rows,'alerts':[a.__dict__ for a in s.query(Alert).filter_by(user_id=u.id).all()],'ai':{'score':87,'verdict':'偏多但不追高：技術面維持強勢，籌碼需觀察法人續買與成交量是否放大。權證部位建議控管時間價值與流動性。','factors':['趨勢向上','AI/PCB/半導體概念強','NASDAQ 連動高','權證流動性風險','月營收需追蹤']},'related':[{'theme':'AI伺服器/PCB','stocks':['2313 華通','2383 台光電','6669 緯穎','2356 英業達']},{'theme':'半導體/美股連動','stocks':['2330 台積電','NVDA','AMD','MU']},{'theme':'高股息/市值型ETF','stocks':['0050','006208','00923','00830']}],'market_impact':[{'name':'NASDAQ','impact':82},{'name':'S&P500','impact':70},{'name':'VIX','impact':-42},{'name':'美元','impact':-20},{'name':'台股加權','impact':76}],'chart':chart}
@app.post('/holdings')
def add_holding(x:HoldingIn,u:User=Depends(me),s:Session=Depends(db)):
    h=Holding(user_id=u.id,**x.model_dump());s.add(h);s.commit();return {'ok':True,'id':h.id}
@app.post('/alerts')
def add_alert(x:AlertIn,u:User=Depends(me),s:Session=Depends(db)):
    a=Alert(user_id=u.id,**x.model_dump());s.add(a);s.commit();return {'ok':True,'id':a.id}
@app.post('/line/test')
def line_test(message:str='BullStreet AI test push',u:User=Depends(me)):
    if not LINE_TOKEN or not LINE_USER_ID: return {'ok':False,'message':'LINE token/user id not configured'}
    r=requests.post('https://api.line.me/v2/bot/message/push',headers={'Authorization':f'Bearer {LINE_TOKEN}','Content-Type':'application/json'},json={'to':LINE_USER_ID,'messages':[{'type':'text','text':message}]})
    return {'ok':r.status_code<300,'status':r.status_code,'body':r.text}
@app.get('/health')
def health(): return {'ok':True,'service':'BullStreet AI'}
