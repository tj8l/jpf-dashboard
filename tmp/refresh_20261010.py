import json, re
from datetime import date, datetime, timedelta
NOW="2026-10-10T05:12:00-07:00"; NOWL="Sat Oct 10, 2026 · 5:12 AM PT"
cal=json.load(open('calendar.json'))
cal['fetchedAt']=NOW
cal['notes']=[
 "Today Sat Oct 10: U15 C4 Development with C1 10:45–11:45 AM @ LEC 3; Work · MMA A 4:00 PM–12:00 AM overlaps U17 League at Abbotsford 9:15–11:15 PM (Abbotsford Rec Centre).",
 "Sun Oct 11 CLASH: U15 C4 Game at C1 5:15–6:45 PM PT @ LEC 2 overlaps U17 League vs Abbotsford 6:15–8:15 PM PT @ LEC 1.",
 "Weekly U17 Development Wednesdays 7:00–8:00 PM PT @ LEC 2, Oct 14 through Dec 16; Wed Oct 28 overlaps U15 C4 at Semiahmoo C4 (7:45 PM, Newton Arena); Wed Nov 4 during MMA A shift.",
 "Sat Dec 5 U17 League vs North Vancouver 4:45–6:15 PM PT @ Harry Jerome overlaps MMA A shift.",
 "Weekbar Sat Oct 10–Fri Oct 16: MMA A Sat (green); U15 C4 orange (Development Sat, Game Sun at C1, Practice Tue 6 AM); U17 yellow (League Abbotsford Sat + Sun, Practice Mon + Thu, Development Wed, League at Cloverdale Fri 8:45 PM).",
 "No MMA shifts on Google Calendar after Sat Oct 10 until Wed Nov 4. Wed Oct 21 502 General Meeting 6–7 PM.",
 "TeamSnap LANGLEY MHA U17 A1 + U15 C4 are source of truth for both teams' ice through Mar 20, 2027; MMA, personal, and PCAHA meetings preserved (PCAHA from Bulletin #5)."
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
  price=float(j(f'{s}_spot.json')['data']['amount'])
  st=j(f'{s}_stats.json')
  ch=round((float(st['last'])-float(st['open']))/float(st['open'])*100,2) if 'open' in st else 0.0
  w.update(price=round(price,5) if price<1 else round(price,2), change24h=ch, asOf=NOW); crypto[s]=(price,ch)
b24=round((float(bst['last'])-float(bst['open']))/float(bst['open'])*100,2)
d['bitcoinDetail'].update(price=round(btc),change24h=b24,high24h=round(float(bst['high'])),low24h=round(float(bst['low'])),asOf=NOW)
d['meta'].update(lastUpdated=NOW,lastUpdatedLabel=NOWL,updatedBy="assistant-scheduled-refresh")
today=date(2026,10,10); ws=today-timedelta(days=(today.weekday()-5)%7)
if d.get('habitWeekStart')!=ws.isoformat():
  d['habitWeekStart']=ws.isoformat()
  for h in d['habits']: h['week']=[False]*7
w=j('weather_om.json'); dd=w['daily']; cur=w['current']
hi,lo=round(dd['temperature_2m_max'][0]),round(dd['temperature_2m_min'][0]); rain=dd['precipitation_probability_max'][0]
cC=round(cur['temperature_2m']); F=lambda c: round(c*9/5+32)
temp=dict(highC=hi,lowC=lo,highF=F(hi),lowF=F(lo),displayC=f"{hi}° / {lo}°C",displayF=f"{F(hi)}° / {F(lo)}°F",currentC=cC,currentF=F(cC))
wx=json.load(open('weather.json'))
wk=round(dd['wind_speed_10m_max'][0])
wx.update(date="2026-10-10",dateLabel="Sat Oct 10, 2026",
 conditions=f"Dry and overcast today (rain ~{rain}%), light winds; ~{cC}°C now, high ~{hi}°C / low ~{lo}°C. Sun clear and mild ~{round(dd['temperature_2m_max'][1])}/{round(dd['temperature_2m_min'][1])}°C; Mon cloudy ~{round(dd['temperature_2m_max'][2])}/{round(dd['temperature_2m_min'][2])}°C.",
 conditionsShort="Overcast, dry",temp=temp,rainChancePct=rain,
 wind=dict(summary="light",maxKmh=wk,display=f"Light, ~{wk} km/h"),
 sun=dict(sunrise=dd['sunrise'][0][-5:],sunset=dd['sunset'][0][-5:],sunriseLabel="7:24 AM",sunsetLabel="6:30 PM",timezoneNote="PT"),
 asOf=NOW,asOfLabel=NOWL,source="Open-Meteo (Langley BC)",lastUpdated=NOW)
json.dump(wx,open('weather.json','w'),indent=2,ensure_ascii=False)
d['weather'].update(conditionsShort=wx['conditionsShort'],temp=temp,rainChancePct=rain,asOf=NOW,asOfLabel=NOWL)
c=crypto
d['news']=[
 {"title":f"BTC ~${btc:,.0f} ({fmt(bp)} vs Fri snap; {fmt(b24)} 24h)","source":"Coinbase","date":"2026-10-10","dateLabel":"Oct 10","url":"https://www.coinbase.com/price/bitcoin"},
 {"title":f"FET ~${c['fet'][0]:.4f} ({fmt(c['fet'][1])} 24h); ETH ~${c['eth'][0]:,.0f} ({fmt(c['eth'][1])}); SOL ~${c['sol'][0]:.2f} ({fmt(c['sol'][1])}); NEAR ~${c['near'][0]:.3f} ({fmt(c['near'][1])})","source":"Coinbase","date":"2026-10-10","dateLabel":"Oct 10","url":"https://www.coinbase.com/price/fetch"},
 {"title":f"Gold ~${gold:,.0f} ({fmt(gp)}); WTI ~${wti:.2f} ({fmt(wp)}); SPX {spx:,.2f} ({fmt(sp)} Fri close); US10Y {tnx:.2f}%","source":"gold-api / Yahoo","date":"2026-10-10","dateLabel":"Oct 10","url":"https://finance.yahoo.com/quote/%5EGSPC"},
 {"title":"No TeamSnap changes. Today U17 at Abbotsford 9:15 PM overlaps MMA A; Sun Oct 11 U15 C4 at C1 vs U17 League clash still on","source":"TeamSnap / LMHA","date":"2026-10-10","dateLabel":"Oct 10","url":"https://www.teamsnap.com/"},
]
json.dump(d,open('data.json','w'),indent=2,ensure_ascii=False)
mk=json.load(open('markets.json'))
mk['asOf']=NOW; mk['note']="Fri pre-market PT — gold live gold-api; WTI Yahoo (live futures); SPX/US10Y Yahoo (Fri close); BTC Coinbase"
mp={'gold':'xau','oil':'wti','btc':'btc','spx':'spx','us10y':'us10y'}
for s in mk['spots']:
  u=upd[mp[s['id']]]; s.update(value=u['value'],change=u['changeDisplay'],asOf="2026-10-10",status="live")
json.dump(mk,open('markets.json','w'),indent=2,ensure_ascii=False)
print(dict(btc=(btc,bp,b24),gold=(gold,gp),wti=(wti,wp),spx=(spx,sp),tnx=(tnx,tp),crypto=c,wx=(cC,hi,lo,rain,wk)))
