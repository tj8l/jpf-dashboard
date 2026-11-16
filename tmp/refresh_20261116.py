import json
from datetime import date, timedelta
NOW="2026-11-16T05:00:00-07:00"; NOWL="Mon Nov 16, 2026 · ~5:00 AM PT"
cal=json.load(open('calendar.json'))
cal['fetchedAt']=NOW
for e in cal['events']:
  for k in('start','end'):
    if e[k].endswith('-08:00'): e[k]=e[k][:-6]+'-07:00'
cal['events'].sort(key=lambda e:e['start'])
cal['range']=dict(start="2026-11-16",end="2026-11-22",label="Nov 16–22 (next 7 days)")
cal['notes']=[
 "Today Mon Nov 16: U17 League vs South Delta 7:30 PM (South Delta). Tue Nov 17: U15 C4 Practice 6 AM SPX 2. Wed Nov 18: U17 Development 7 PM LEC 2. Thu Nov 19: NEW U15 C4 Practice 6:15 PM SPX 1; U17 Practice 9:15 PM SPX 2. Fri Nov 20: U17 Dryland 8:30 PM Aim Athletic. Sat Nov 21: U15 C4 Development with C1 10:45 AM LEC 3; U15 C4 at South Delta C3 4:30 PM. Sun Nov 22: U17 League vs North Vancouver 6:15 PM LEC 1 + U15 C4 vs Cloverdale C2 6:15 PM Cloverdale Sport & Ice Complex.",
 "TeamSnap overnight: new U15 C4 Practice Thu Nov 19 6:15–7:30 PM at SPX 1. Sun Nov 15 games aged out. No other changes.",
 "Clash: Sun Nov 22 U17 League vs North Vancouver 6:15 PM LEC 1 and U15 C4 at Cloverdale 6:15 PM start at the same time, different venues (now inside the 7-day window).",
 "Google Calendar: no new items; stale U15 Google items and TBD slots stay excluded. Leftover -08:00 offsets on Google events normalized to -07:00 (same wall clock).",
 "MMA A block Dec 3-8 overlaps U17 Practice Dec 3 + Dec 7, Dryland Dec 4, League vs North Vancouver Sat Dec 5 4:45 PM, and HOLD LEC 1 Dec 6.",
 "TeamSnap LANGLEY MHA U17 A1 + U15 C4 are source of truth for both teams' ice through Mar 20, 2027; MMA, personal, and PCAHA meetings preserved."
]
json.dump(cal,open('calendar.json','w'),indent=2,ensure_ascii=False); open('calendar.json','a').write("\n")

def j(p): return json.load(open('tmp/'+p))
btc=float(j('btc_spot.json')['data']['amount']); bst=j('btc_stats.json')
gold=float(j('gold.json')['price'])
def ych(f):
  r=j(f)['chart']['result'][0]; c=[x for x in r['indicators']['quote'][0]['close'] if x is not None]
  return c[-1], c[-2]
wti,wtip=ych('y_CLF.json'); spx,spxp=ych('y_GSPC.json'); tnx,tnxp=ych('y_TNX.json')
d=json.load(open('data.json'))
prev={m['id']:m['value'] for m in d['primaryMarkets']}
pct=lambda a,b: round((a-b)/b*100,2)
fmt=lambda p: ("+" if p>=0 else "")+f"{p:.2f}%"
gp=pct(gold,prev['xau']); bp=pct(btc,prev['btc']); wp=pct(wti,wtip); sp=pct(spx,spxp); tp=round(tnx-tnxp,3)
upd={
 'xau':dict(value=round(gold,1),display=f"${gold:,.0f}",change=round(gold-prev['xau'],1),changePct=gp,changeDisplay=fmt(gp)+" vs prior snap",source="gold-api.com"),
 'wti':dict(value=round(wti,2),display=f"${wti:.2f}",change=round(wti-wtip,2),changePct=wp,changeDisplay=fmt(wp)+" vs prior close",source="Yahoo CL=F"),
 'btc':dict(value=round(btc),display=f"${btc:,.0f}",change=round(btc-prev['btc']),changePct=bp,changeDisplay=fmt(bp)+" vs prior snap",source="Coinbase"),
 'spx':dict(value=round(spx,2),display=f"{spx:,.2f}",change=round(spx-spxp,2),changePct=sp,changeDisplay=fmt(sp)+" vs prior close",source="Yahoo ^GSPC"),
 'us10y':dict(value=round(tnx,3),display=f"{tnx:.2f}%",change=tp,changePct=pct(tnx,tnxp),changeDisplay=("+" if tp>=0 else "")+f"{tp:.2f} pts vs prior close",source="Yahoo ^TNX"),
}
for m in d['primaryMarkets']:
  m.update(upd[m['id']]); m['asOf']=NOW
crypto={}
for w in d['watchlist']:
  s=w['id']
  if s=='usdc':
    w.update(asOf=NOW); crypto[s]=(w.get('price',1.0), w.get('change24h',0.0)); continue
  price=float(j(f'{s}_spot.json')['data']['amount'])
  try:
    st=j(f'{s}_stats.json')
    ch=round((float(st['last'])-float(st['open']))/float(st['open'])*100,2) if 'open' in st and 'last' in st else 0.0
  except Exception:
    ch=0.0
  w.update(price=round(price,5) if price<1 else round(price,2), change24h=ch, asOf=NOW); crypto[s]=(price,ch)
b24=round((float(bst['last'])-float(bst['open']))/float(bst['open'])*100,2)
d['bitcoinDetail'].update(price=round(btc),change24h=b24,high24h=round(float(bst['high'])),low24h=round(float(bst['low'])),asOf=NOW)
d['meta'].update(lastUpdated=NOW,lastUpdatedLabel=NOWL,updatedBy="assistant-scheduled-refresh")
today=date(2026,11,16); ws=today-timedelta(days=(today.weekday()-5)%7)
if d.get('habitWeekStart')!=ws.isoformat():
  d['habitWeekStart']=ws.isoformat()
  for h in d['habits']: h['week']=[False]*7
w=j('weather_om.json'); dd=w['daily']; cur=w['current']
hi,lo=round(dd['temperature_2m_max'][0]),round(dd['temperature_2m_min'][0]); rain=dd['precipitation_probability_max'][0]
cC=round(cur['temperature_2m']); F=lambda c: round(c*9/5+32)
temp=dict(highC=hi,lowC=lo,highF=F(hi),lowF=F(lo),displayC=f"{hi}° / {lo}°C",displayF=f"{F(hi)}° / {F(lo)}°F",currentC=cC,currentF=F(cC))
wx=json.load(open('weather.json'))
wk=round(dd['wind_speed_10m_max'][0])
pp=dd['precipitation_probability_max']
wx.update(date="2026-11-16",dateLabel="Mon Nov 16, 2026",
 conditions=f"Monday: high ~{hi}°C / low ~{lo}°C, rain ~{rain}%, wind ~{wk} km/h. Tue (~{pp[1]}%), Wed (~{pp[2]}%).",
 conditionsShort="Cool",temp=temp,rainChancePct=rain,
 wind=dict(summary="light",maxKmh=wk,display=f"Light, ~{wk} km/h"),
 sun=dict(sunrise="08:22",sunset="17:27",sunriseLabel="8:22 AM",sunsetLabel="5:27 PM",timezoneNote="PT"),
 asOf=NOW,asOfLabel=NOWL,source="Open-Meteo (Langley BC)",lastUpdated=NOW)
json.dump(wx,open('weather.json','w'),indent=2,ensure_ascii=False)
d['weather'].update(conditionsShort=wx['conditionsShort'],temp=temp,rainChancePct=rain,asOf=NOW,asOfLabel=NOWL)
c=crypto
d['news']=[
 {"title":f"BTC ~${btc:,.0f} ({fmt(bp)} vs prior snap; {fmt(b24)} 24h) — 24h low ~${float(bst['low']):,.0f}","source":"Coinbase","date":"2026-11-16","dateLabel":"Nov 16","url":"https://www.coinbase.com/price/bitcoin"},
 {"title":f"Agent basket: NEAR ~${c['near'][0]:.3f} ({fmt(c['near'][1])} 24h); FET ~${c['fet'][0]:.4f} ({fmt(c['fet'][1])}); SOL ~${c['sol'][0]:.2f} ({fmt(c['sol'][1])}); ETH ~${c['eth'][0]:,.0f} ({fmt(c['eth'][1])})","source":"Coinbase","date":"2026-11-16","dateLabel":"Nov 16","url":"https://www.coinbase.com/price/near"},
 {"title":f"Gold ~${gold:,.0f} ({fmt(gp)}); WTI ~${wti:.2f} ({fmt(wp)} futures vs prior close); SPX {spx:,.2f} ({fmt(sp)}); US10Y {tnx:.2f}%","source":"gold-api / Yahoo","date":"2026-11-16","dateLabel":"Nov 16","url":"https://finance.yahoo.com/quote/%5EGSPC"},
 {"title":"Today: U17 League vs South Delta 7:30 PM. New: U15 C4 Practice Thu Nov 19 6:15 PM SPX 1.","source":"TeamSnap / LMHA","date":"2026-11-16","dateLabel":"Nov 16","url":"https://www.teamsnap.com/"},
]
json.dump(d,open('data.json','w'),indent=2,ensure_ascii=False)
mk=json.load(open('markets.json'))
mk['asOf']=NOW; mk['note']="Mon pre-open PT — gold live (gold-api); WTI futures vs prior close (Yahoo); SPX/US10Y latest close (US cash market not open yet); BTC Coinbase"
mp={'gold':'xau','oil':'wti','btc':'btc','spx':'spx','us10y':'us10y'}
for s in mk['spots']:
  u=upd[mp[s['id']]]; s.update(value=u['value'],change=u['changeDisplay'],asOf="2026-11-16",status="live")
json.dump(mk,open('markets.json','w'),indent=2,ensure_ascii=False)
print(dict(btc=(btc,bp,b24),gold=(gold,gp),wti=(wti,wp),spx=(spx,sp),tnx=(tnx,tp),crypto=c,wx=(cC,hi,lo,rain,wk),habitWeek=d.get('habitWeekStart'),wti_vs_snap=pct(wti,prev['wti']),spx_vs_snap=pct(spx,prev['spx'])))
