import json
from datetime import date, timedelta
NOW="2026-11-08T05:15:00-08:00"; NOWL="Sun Nov 8, 2026 · ~5:15 AM PT"
cal=json.load(open('calendar.json'))
cal['fetchedAt']=NOW

# Restore hand-enriched TeamSnap labels/venues/whenLabels TeamSnap stripped overnight
MLC='Mission Leisure Centre (7650 Grand St, Mission)'
enrich={
 'ts-u15-10816643-376175568':('U15 C4 Fallen Stars (Mission) · vs Semiahmoo C2',MLC+' – South','Sun Nov 8 · 1:00 PM–2:15 PM PT (arrive 12:15 PM)'),
 'ts-u15-10816643-375553804':('U15 C4 Game · vs C2 (Pink Pigeons)','LEC 2 (Langley Events Centre)',None),
 'ts-u15-10816643-375553645':('U15 C4 Game · vs C3 (Havoc)','LEC 2 (Langley Events Centre)',None),
 'ts-u15-10816643-375553658':('U15 C4 Game · vs C3 (Havoc)','LEC 2 (Langley Events Centre)',None),
 'ts-u15-10816643-376174991':('U15 C4 Game · at Semiahmoo C3','South Surrey Arena (2199 148 St, Surrey)','Sat Nov 14 · 8:00 PM–9:15 PM PT (arrive 7:15 PM)'),
 'ts-u15-10816643-376175057':('U15 C4 Game · at South Delta C3','South Delta Rec Centre – Main Rink (1720 56th St, Delta)','Sat Nov 21 · 4:30 PM–6:00 PM PT (arrive 3:45 PM)'),
 'ts-u17-10808348-375456404':('U17 Abbotsford #3 · vs West Kelowna U18 A2','Summit Centre – West (3600 Townline Rd, Abbotsford)','Sun Nov 8 · 9:00 AM–11:00 AM PT (arrive 8:00 AM, White — bring both)'),
 'ts-u17-10808348-374267019':('U17 Abbotsford Tournament · playoff day','Matsqui Recreation Centre (3106 Clearbrook Rd, Abbotsford)','Mon Nov 9 · 7:45 AM–7:45 PM PT (playoff hold: 7v8 7:45, 5v6 10:00 at MRC; semis 12:15–2:15 at MRC / Summit Centre West; gold 5–7 PM at MSA Arena)'),
}
for e in cal['events']:
  if e['id'] in enrich:
    s,loc,wl=enrich[e['id']]
    e['summary']=s
    if loc: e['location']=loc
    if wl: e['whenLabel']=wl

cal['events'].sort(key=lambda e:e['start'])
cal['range']=dict(start="2026-11-08",end="2026-11-14",label="Nov 8–14 (next 7 days)")
cal['notes']=[
 "Today Sun Nov 8: U17 Abbotsford vs West Kelowna 9:00 AM (Summit West, arrive 8:00, White) + U15 Fallen Stars vs Semiahmoo C2 1:00–2:15 PM (Mission Leisure Centre South, arrive 12:15) + MMA A 4 PM. Cooler with showers (rain ~71%, wind ~29 km/h, high ~12°C / low ~5°C).",
 "Mon Nov 9: U17 Abbotsford playoff day 7:45 AM–7:45 PM (Matsqui; semis 12:15–2:15 MRC/Summit West; gold 5–7 PM MSA), then U17 Practice 9:30 PM SPX 2. Tue Nov 10: U15 C4 Practice 6 AM SPX 2. Wed Nov 11: U17 League vs Ridge Meadows 8:45 PM (away). Thu Nov 12: U17 League vs Ridge Meadows 9:15 PM SPX 2. Fri Nov 13: U15 vs Pink Pigeons (C2) 7 PM LEC 2, then U17 Dryland 8:30 PM. Sat Nov 14: U15 at Semiahmoo C3 8:00 PM South Surrey Arena (arrive 7:15).",
 "TeamSnap overnight: replaced the all-day U15 Fallen Stars TBD crossover with a timed game vs Semiahmoo C2, Sun Nov 8 1:00–2:15 PM @ Mission Leisure Centre South (arrive 12:15). Added U15 at Semiahmoo C3, Sat Nov 14 8:00–9:15 PM @ South Surrey Arena (arrive 7:15), and U15 at South Delta C3, Sat Nov 21 4:30–6:00 PM @ South Delta Rec Centre Main (arrive 3:45). U17 unchanged (Saturday’s vs Squamish aged out). Stripped Fallen Stars / Abbotsford # labels and collapsed rink names again (restored on board). Upcoming: U17 38, U15 C4 10.",
 "U15 C4 November (TeamSnap): Tue practices 6 AM SPX 2 Nov 10/17; Fri Nov 13 vs Pink Pigeons (C2) 7 PM LEC 2; Sat Nov 14 at Semiahmoo C3 8 PM South Surrey Arena; Sun Nov 15 + Nov 22 vs C3 Havoc 7 PM LEC 2; Sat Nov 21 Development with C1 10:45 AM LEC 3 and at South Delta C3 4:30 PM; Sat Nov 28 Development with C2 10:45 AM LEC 3.",
 "Clashes: Sun Nov 15 and Nov 22 U15 7 PM LEC 2 overlap U17 League 6:15 PM LEC 1; Fri Nov 13 U15 7–8:30 PM runs into U17 Dryland 8:30 PM. Sat Nov 21 is a double for U15 (development morning, South Delta afternoon) but the times do not overlap.",
 "Google Calendar unchanged vs Sat aside from Saturday items aging out; still has the all-day Fallen Stars crossover TBD (TeamSnap now has the 1:00 PM Semiahmoo C2 game), stale U15 items TeamSnap dropped or replaced (C3/C4 slots Nov 8/29, practices Nov 24 and Dec 1, times one hour early) — TeamSnap stays on the board. Google does not yet list the new Nov 14 Semiahmoo C3 or Nov 21 South Delta C3 games, or the Nov 28 Development with C2.",
 "Abbotsford Winter Extreme Ski & Board Sale, Sat–Sun Nov 14–15, Ag-Rec Centre (hours not posted).",
 "Weekly U17 Development Wednesdays 7:00–8:00 PM PT @ LEC 2 through Dec 16 (no session Nov 11).",
 "MMA A block Dec 3–8 overlaps U17 Practice Dec 3 + Dec 7, Dryland Dec 4, League vs North Vancouver Sat Dec 5 4:45 PM, and HOLD LEC 1 Dec 6.",
 "Mon Nov 16 U17 League vs South Delta 9:00 PM overlaps U17 Practice 9:30 PM @ SPX 2 (TeamSnap — likely practice replaced by game).",
 "Weekbar Sun Nov 8–Sat Nov 14: MMA A green Sunday (U17/U15 tournament); U17 yellow Mon + Wed + Thu; U15 orange Tue + Fri + Sat.",
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
today=date(2026,11,8); ws=today-timedelta(days=(today.weekday()-5)%7)
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
wx.update(date="2026-11-08",dateLabel="Sun Nov 8, 2026",
 conditions=f"Cooler Sunday with showers: high ~{hi}°C / low ~{lo}°C, rain ~{rain}%, wind ~{wk} km/h. Mon–Tue wetter (rain ~{pp[1]}–{pp[2]}%, highs ~{round(dd['temperature_2m_max'][1])}°C); Wed milder, high ~{round(dd['temperature_2m_max'][3])}°C still a good chance of rain; Thu–Sat lingering showers.",
 conditionsShort="Cooler, showers, breezy",temp=temp,rainChancePct=rain,
 wind=dict(summary="breezy",maxKmh=wk,display=f"Breezy, ~{wk} km/h"),
 sun=dict(sunrise=dd['sunrise'][0][-5:],sunset=dd['sunset'][0][-5:],sunriseLabel="7:09 AM",sunsetLabel="4:38 PM",timezoneNote="PT"),
 asOf=NOW,asOfLabel=NOWL,source="Open-Meteo (Langley BC)",lastUpdated=NOW)
json.dump(wx,open('weather.json','w'),indent=2,ensure_ascii=False)
d['weather'].update(conditionsShort=wx['conditionsShort'],temp=temp,rainChancePct=rain,asOf=NOW,asOfLabel=NOWL)
c=crypto
d['news']=[
 {"title":f"BTC ~${btc:,.0f} ({fmt(bp)} vs Sat snap; {fmt(b24)} 24h) — quiet weekend, holding after Friday’s drop","source":"Coinbase","date":"2026-11-08","dateLabel":"Nov 8","url":"https://www.coinbase.com/price/bitcoin"},
 {"title":f"Agent basket: NEAR ~${c['near'][0]:.3f} ({fmt(c['near'][1])} 24h); FET ~${c['fet'][0]:.4f} ({fmt(c['fet'][1])}); SOL ~${c['sol'][0]:.2f} ({fmt(c['sol'][1])}); ETH ~${c['eth'][0]:,.0f} ({fmt(c['eth'][1])})","source":"Coinbase","date":"2026-11-08","dateLabel":"Nov 8","url":"https://www.coinbase.com/price/near"},
 {"title":f"Gold ~${gold:,.0f} ({fmt(gp)}); WTI ~${wti:.2f} ({fmt(wp)} futures vs prior close); SPX {spx:,.2f} ({fmt(sp)} Fri close); US10Y {tnx:.2f}%","source":"gold-api / Yahoo","date":"2026-11-08","dateLabel":"Nov 8","url":"https://finance.yahoo.com/quote/%5EGSPC"},
 {"title":"Today: U17 Abbotsford vs West Kelowna 9:00 AM (Summit West), U15 Fallen Stars vs Semiahmoo C2 1:00 PM (Mission South), MMA A 4 PM. Cooler, showers.","source":"TeamSnap / LMHA","date":"2026-11-08","dateLabel":"Nov 8","url":"https://www.teamsnap.com/"},
]
json.dump(d,open('data.json','w'),indent=2,ensure_ascii=False)
mk=json.load(open('markets.json'))
mk['asOf']=NOW; mk['note']="Sun morning PT — gold gold-api; WTI/SPX/US10Y Fri close (Yahoo); BTC Coinbase"
mp={'gold':'xau','oil':'wti','btc':'btc','spx':'spx','us10y':'us10y'}
for s in mk['spots']:
  u=upd[mp[s['id']]]; s.update(value=u['value'],change=u['changeDisplay'],asOf="2026-11-08",status="live")
json.dump(mk,open('markets.json','w'),indent=2,ensure_ascii=False)
print(dict(btc=(btc,bp,b24),gold=(gold,gp),wti=(wti,wp),spx=(spx,sp),tnx=(tnx,tp),crypto=c,wx=(cC,hi,lo,rain,wk),habitWeek=d.get('habitWeekStart'),wti_vs_snap=pct(wti,prev['wti']),spx_vs_snap=pct(spx,prev['spx'])))
