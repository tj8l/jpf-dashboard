import json, re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
NOW="2026-10-07T05:14:00-07:00"; NOWL="Wed Oct 7, 2026 · 5:14 AM PT"
cal=json.load(open('calendar.json'))
ev=cal['events']; ids={e['id'] for e in ev}
adds=[
 {"id":"k25vomtn45f2be51piomtt3ivs","summary":"U15 C4 Game — vs South Delta C1 (HOME)","location":"LEC (The Arenas at Langley Events Centre)","start":"2026-10-25T19:00:00-07:00","end":"2026-10-25T20:30:00-07:00","whenLabel":"Sun Oct 25 · 7:00 PM–8:30 PM PT","description":"Game U15Q6079. Arrive 6:15 PM. From TeamSnap (via Google Calendar)."},
 {"id":"fi7468294jbsbb80h762r3sfqc","summary":"U15 C4 Game — at Semiahmoo C4","location":"Newton Arena (Surrey), Main Rink","start":"2026-10-28T19:45:00-07:00","end":"2026-10-28T21:15:00-07:00","whenLabel":"Wed Oct 28 · 7:45 PM–9:15 PM PT","description":"Game U15Q6080. Arrive 7:00 PM. Newton Arena, 7120 136B Street, Surrey. From TeamSnap (via Google Calendar)."},
]
for a in adds:
  if a['id'] not in ids: ev.append(a)
ev.sort(key=lambda e:e['start'])
cal['events']=ev
cal['fetchedAt']=NOW
cal['notes']=[
 "Today Wed Oct 7: Work · MMA A 4:00 PM–12:00 AM.",
 "Sun Oct 11 CLASH: U15 C4 Game — vs C1 5:15–6:45 PM PT @ LEC 2 overlaps U17 League · vs Abbotsford 6:15–8:15 PM PT.",
 "Weekbar Wed Oct 7–Tue Oct 13: MMA A Wed–Sat afternoons (green); U17 yellow (Practice Thu + Mon, Dryland Fri, League Abbotsford Sat + Sun); U15 orange (Interleague Fri, Development Sat, Game Sun, Practice Tue); PCAHA Presidents C Thu 7pm Zoom.",
 "New: Sun Oct 25 U15 C4 vs South Delta C1 (HOME) 7:00–8:30 PM PT @ LEC (arrive 6:15) — same weekend as U17 Winfield tournament HOLD Oct 23–25 (Lake Country).",
 "New: Wed Oct 28 U15 C4 at Semiahmoo C4 7:45–9:15 PM PT @ Newton Arena (arrive 7:00).",
 "Beyond 7-day day-list window: Thu Oct 15 (U17 Practice); Fri Oct 16 (U17 League); Sat Oct 17 (U15 C4 at Cloverdale C3) — still in calendar.json events.",
 "No MMA shifts on Google Calendar after Sat Oct 10 until Nov 4.",
 "TeamSnap LANGLEY MHA U17 A1 is source of truth for U17. Non-U17 (MMA, U15 C) kept from Google Calendar. PCAHA from Bulletin #5. U15 C4 ICS still missing from teamsnap.json — syncing U17 only; U15 ice preserved from Google."
]
json.dump(cal,open('calendar.json','w'),indent=2,ensure_ascii=False); open('calendar.json','a').write("\n")

# markets
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
# habits week rollover (Sat-start week)
today=date(2026,10,7); ws=today-timedelta(days=(today.weekday()-5)%7)
if d.get('habitWeekStart')!=ws.isoformat():
  d['habitWeekStart']=ws.isoformat()
  for h in d['habits']: h['week']=[False]*7
# weather
w=j('weather_om.json'); dd=w['daily']; cur=w['current']
hi,lo=round(dd['temperature_2m_max'][0]),round(dd['temperature_2m_min'][0]); rain=dd['precipitation_probability_max'][0]
cC=round(cur['temperature_2m']); F=lambda c: round(c*9/5+32)
temp=dict(highC=hi,lowC=lo,highF=F(hi),lowF=F(lo),displayC=f"{hi}° / {lo}°C",displayF=f"{F(hi)}° / {F(lo)}°F",currentC=cC,currentF=F(cC))
wx=json.load(open('weather.json'))
wx.update(date="2026-10-07",dateLabel="Wed Oct 7, 2026",
 conditions=f"Foggy start (~{cC}°C), then dry; high ~{hi}°C / low ~{lo}°C; rain chance ~{rain}%. Thu ~{round(dd['temperature_2m_max'][1])}/{round(dd['temperature_2m_min'][1])}°C overcast, rain ~{dd['precipitation_probability_max'][1]}%; Fri rain returns (~{dd['precipitation_probability_max'][2]}%, ~{round(dd['temperature_2m_max'][2])}°C, breezy).",
 conditionsShort="Morning fog, dry",temp=temp,rainChancePct=rain,
 wind=dict(summary="light",maxKmh=round(dd['wind_speed_10m_max'][0]),display=f"Light, ~{round(dd['wind_speed_10m_max'][0])} km/h"),
 sun=dict(sunrise=dd['sunrise'][0][-5:],sunset=dd['sunset'][0][-5:],sunriseLabel="7:19 AM",sunsetLabel="6:36 PM",timezoneNote="PT"),
 asOf=NOW,asOfLabel=NOWL,source="Open-Meteo (Langley BC)",lastUpdated=NOW)
json.dump(wx,open('weather.json','w'),indent=2,ensure_ascii=False)
d['weather'].update(conditionsShort=wx['conditionsShort'],temp=temp,rainChancePct=rain,asOf=NOW,asOfLabel=NOWL)
c=crypto
d['news']=[
 {"title":f"BTC ~${btc:,.0f} ({fmt(bp)} vs Tue snap; {fmt(b24)} 24h)","source":"Coinbase","date":"2026-10-07","dateLabel":"Oct 7","url":"https://www.coinbase.com/price/bitcoin"},
 {"title":f"FET ~${c['fet'][0]:.4f} ({fmt(c['fet'][1])} 24h); ETH ~${c['eth'][0]:,.0f} ({fmt(c['eth'][1])}); SOL ~${c['sol'][0]:.2f} ({fmt(c['sol'][1])}); NEAR ~${c['near'][0]:.3f} ({fmt(c['near'][1])})","source":"Coinbase","date":"2026-10-07","dateLabel":"Oct 7","url":"https://www.coinbase.com/price/fetch"},
 {"title":f"Gold ~${gold:,.0f} ({fmt(gp)}); WTI ~${wti:.2f} ({fmt(wp)}); SPX {spx:,.2f} ({fmt(sp)} Tue close); US10Y {tnx:.2f}%","source":"gold-api / Yahoo","date":"2026-10-07","dateLabel":"Oct 7","url":"https://finance.yahoo.com/quote/%5EGSPC"},
 {"title":"New U15 C4: Sun Oct 25 vs South Delta C1 (HOME, U17 Winfield tournament weekend) and Wed Oct 28 at Semiahmoo. Sun Oct 11 U15/U17 clash still on; U15 C4 ICS still missing","source":"TeamSnap / LMHA","date":"2026-10-07","dateLabel":"Oct 7","url":"https://www.teamsnap.com/"},
]
json.dump(d,open('data.json','w'),indent=2,ensure_ascii=False)
mk=json.load(open('markets.json'))
mk['asOf']=NOW; mk['note']="Wed pre-market PT — gold live gold-api; WTI Yahoo (live futures); SPX/US10Y Yahoo (Tue close); BTC Coinbase"
mp={'gold':'xau','oil':'wti','btc':'btc','spx':'spx','us10y':'us10y'}
for s in mk['spots']:
  u=upd[mp[s['id']]]; s.update(value=u['value'],change=u['changeDisplay'],asOf="2026-10-07",status="live")
json.dump(mk,open('markets.json','w'),indent=2,ensure_ascii=False)
print(dict(btc=(btc,bp,b24),gold=(gold,gp),wti=(wti,wp),spx=(spx,sp),tnx=(tnx,tp),crypto=c,wx=(cC,hi,lo,rain)))
