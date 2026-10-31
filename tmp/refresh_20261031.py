import json, re
from datetime import date, datetime, timedelta
NOW="2026-10-31T05:15:00-07:00"; NOWL="Sat Oct 31, 2026 · 5:15 AM PT"
cal=json.load(open('calendar.json'))
cal['fetchedAt']=NOW
# Align Google MMA A Nov/Dec shifts with Google's current representation
g={e['id']:e for e in json.load(open('tmp/gcal_events_20261031.json'))['events']}
for e in []:
  if e['id'] in g and 'MMA' in e['summary'] and 'dateTime' in g[e['id']]['start']:
    e['start']=g[e['id']]['start']['dateTime']; e['end']=g[e['id']]['end']['dateTime']
# Mission tournament patches
for e in cal['events']:
  if e['id'].startswith('ts-u15-10816643-37507'):
    e['whenLabel']=e['whenLabel'].split(' · ')[0]+' · time TBD (arrive 12:00 PM) PT'
    e['location']='Mission Leisure Centre (7650 Grand St, Mission)'
# U17 Winfield tournament + Team Photo patches
WIN='Winfield Arena (9830 Bottom Wood Lake Rd, Lake Country)'
fix={
 'ts-u17-10808348-375563260':('U17 Winfield · vs TriCity U18 A2 (semifinal slot)',WIN,'arrive 5:15 AM, Maroon'),
 'ts-u17-10808348-375167995':('U17 HOLD · Gold Medal Game',WIN,'arrive 11:45 AM'),
 'ts-u17-10808348-375253591':('U17 Team Photo','George Preston Recreation Centre (20699 42 Ave, Langley)','arrive noon, Maroon, full gear + stick, no skates/helmet/neck guard'),
}
for e in cal['events']:
  if e['id'] in fix:
    e['summary'],e['location'],extra=fix[e['id']]
    if extra not in e['whenLabel']: e['whenLabel']=e['whenLabel']+' ('+extra+')'
cal['range']=dict(start="2026-10-31",end="2026-11-06",label="Oct 31–Nov 6 (next 7 days)")
MLC='Mission Leisure Centre (7650 Grand St, Mission)'
fs={
 'ts-u15-10816643-375830212':('U15 C4 Fallen Stars (Mission) · vs Vancouver Thunderbirds U15C6',MLC+' – South','arrive 5:30 PM'),
 'ts-u15-10816643-375830324':('U15 C4 Fallen Stars (Mission) · at Port Coquitlam U15C3',MLC+' – North','arrive 8:30 AM'),
 'ts-u15-10816643-375830513':('U15 C4 Fallen Stars (Mission) · at Vancouver C1',MLC+' – North','arrive 1:00 PM'),
 'ts-u15-10816643-375553616':(None,None,'arrive 6:15 PM'),
 'ts-u15-10816643-375273529':(None,None,'arrive 1:00 PM'),
}
for e in cal['events']:
  if e['id'] in fs:
    a,b,x=fs[e['id']]
    if a: e['summary']=a
    if b: e['location']=b
    if x not in e['whenLabel']: e['whenLabel']+=' ('+x+')'
if not any(e['id']=='klvm6aqf51ag0j0prntpijgasc' for e in cal['events']):
  cal['events'].append(dict(id='klvm6aqf51ag0j0prntpijgasc',summary='Dentist – Fort Langley Dental Office',location='Fort Langley Dental Office',start='2026-11-06T09:20:00-08:00',end='2026-11-06T10:20:00-08:00',whenLabel='Fri Nov 6 · 9:20 AM–10:20 AM PT (confirm by text reply or 604-888-3811)'))
for e in cal['events']:
  if e['id']=='ts-u15-10816643-375390752':
    e['summary']='U15 C4 Practice · George Preston Rec Centre'
    e['location']='George Preston Recreation Centre (20699 42 Ave, Langley)'
    if 'arrive 10:45' not in e['whenLabel']: e['whenLabel']=e['whenLabel']+' (arrive 10:45 AM; overlaps U17 Team Photo 12:00 same venue)'
# Abbotsford tournament: TeamSnap entered these with TZID America/Vancouver; keep typed wall times on the board's Pacific convention
ab={
 'ts-u17-10808348-375456255':('U17 Abbotsford #1 · vs Penticton U18 A2','Matsqui Recreation Centre (3106 Clearbrook Rd, Abbotsford)','2026-11-06T14:45:00-08:00','2026-11-06T16:45:00-08:00','Fri Nov 6 · 2:45 PM–4:45 PM PT (arrive 1:45 PM, White — bring both)'),
 'ts-u17-10808348-375456336':('U17 Abbotsford #2 · vs Squamish U18 A2','MSA Arena (2323 Emerson St, Abbotsford)','2026-11-07T10:15:00-08:00','2026-11-07T12:15:00-08:00','Sat Nov 7 · 10:15 AM–12:15 PM PT (arrive 9:15 AM, Maroon — bring both)'),
 'ts-u17-10808348-375456404':('U17 Abbotsford #3 · vs West Kelowna U18 A2','Summit Centre – West (3600 Townline Rd, Abbotsford)','2026-11-08T09:00:00-08:00','2026-11-08T11:00:00-08:00','Sun Nov 8 · 9:00 AM–11:00 AM PT (arrive 8:00 AM, White — bring both)'),
}
for e in cal['events']:
  if e['id'] in ab: e['summary'],e['location'],e['start'],e['end'],e['whenLabel']=ab[e['id']]
if not any(e['id']=='7vco3epcilqssjvuctejjun98g' for e in cal['events']):
  cal['events'].append(dict(id='7vco3epcilqssjvuctejjun98g',summary='Zoom call with Bruce (Your Life Is the Ceremony)',location='Zoom / Skool',start='2026-11-04T16:00:00-08:00',end='2026-11-04T17:00:00-08:00',whenLabel='Wed Nov 4 · 4:00 PM–5:00 PM PT'))
cal['events'].sort(key=lambda e:e['start'])
cal['notes']=[
 "Today Sat Oct 31: U17 League vs Vancouver TBirds 5:00–7:00 PM @ Hillcrest Centre Arena. Clear and cool, 12°/3°C.",
 "TeamSnap change: U15 C4 Fallen Stars tournament (Mission Leisure Centre) games posted — Fri Nov 6 6:15 PM vs Vancouver Thunderbirds U15C6 (South, arrive 5:30); Sat Nov 7 9:15 AM at Port Coquitlam U15C3 (North, arrive 8:30) and 1:45 PM at Vancouver C1 (North, arrive 1:00). Sun Nov 8 still TBD (arrive noon).",
 "TeamSnap removed: U15 C4 vs C3 Fri Nov 6 7 PM LEC 2 and U15 Development with C1 Sat Nov 7 10:45 AM LEC 3.",
 "Google Calendar's new Fallen Stars entries and 'C4 Team Photo' are one hour early (saved at UTC-7 instead of PST); TeamSnap times are on the board.",
 "Sun Nov 1: U15 C4 Practice 11:15 AM–12:45 PM, U17 Team Photo 12:00–12:30 PM (arrive noon, Maroon, full gear + stick, no skates/helmet/neck guard), U15 C4 Team Photo 1:20 PM (arrive 1:00) — all George Preston Rec Centre; U17 League vs Richmond 6:15 PM @ LEC 1 overlaps U15 at C1 7 PM @ LEC 2 (same building).",
 "Week: Mon Nov 2 U17 League vs North Delta 9:30 PM Sungod; Tue Nov 3 U15 C4 Practice 6 AM SPX 2; Wed Nov 4 MMA A 4 PM + Zoom with Bruce 4 PM + U17 Development 7 PM LEC 2; Thu Nov 5 MMA A 4 PM + U17 Practice 9:15 PM SPX 2; Fri Nov 6 Dentist 9:20 AM Fort Langley Dental.",
 "Nov 6–8 pileup: Fri Nov 6 U17 Abbotsford vs Penticton 2:45 PM + MMA A 4 PM–12 AM + U15 Mission vs TBirds 6:15 PM; Sat Nov 7 U15 Mission 9:15 AM + U17 Abbotsford vs Squamish 10:15 AM + U15 Mission 1:45 PM + MMA A 4 PM; Sun Nov 8 U17 vs West Kelowna 9:00 AM + U15 Mission TBD + MMA A 4 PM.",
 "U15 C4 November (TeamSnap): Tue practices 6 AM SPX 2 Nov 3/10/17; Fri Nov 13 vs C2 7 PM LEC 2; Sun Nov 15 + Nov 22 vs C3 7 PM LEC 2; Sat Nov 21 Development with C1 10:45 AM LEC 3.",
 "Clashes: Sun Nov 15 and Nov 22 U15 7 PM LEC 2 overlap U17 League 6:15 PM LEC 1; Fri Nov 13 U15 vs C2 7–8:30 PM runs into U17 Dryland 8:30 PM; Thu Nov 5 U17 Practice 9:15 PM during MMA A shift.",
 "Google Calendar also has U15 items TeamSnap doesn't yet: C3/C4 game slots (TBD) Sun Nov 8 and Nov 29 7 PM LEC 2, practices Tue Nov 24 and Dec 1 6 AM SPX 2 — not on the board until TeamSnap posts them.",
 "U17 Abbotsford tournament Nov 6–8 — Fri 2:45 PM vs Penticton U18 A2 @ Matsqui Rec (arrive 1:45, White); Sat 10:15 AM vs Squamish U18 A2 @ MSA Arena (arrive 9:15, Maroon); Sun 9:00 AM vs West Kelowna U18 A2 @ Summit Centre West (arrive 8:00, White).",
 "Zoom call with Bruce Wed Nov 4 4–5 PM PT — overlaps MMA A shift (4 PM–12 AM) and comes before U17 Development 7 PM.",
 "Weekly U17 Development Wednesdays 7:00–8:00 PM PT @ LEC 2 through Dec 16 (no session Nov 11).",
 "MMA A block Dec 3–8 overlaps U17 Practice Dec 3 + Dec 7, Dryland Dec 4, League vs North Vancouver Sat Dec 5 4:45 PM, and HOLD LEC 1 Dec 6.",
 "Mon Nov 16 U17 League vs South Delta 9:00 PM overlaps U17 Practice 9:30 PM @ SPX 2 (TeamSnap — likely practice replaced by game).",
 "Weekbar Sat Oct 31–Fri Nov 6: U17 yellow (vs TBirds Sat 5 PM, vs North Delta Mon 9:30 PM); U15 orange (Practice + Team Photo + at C1 Sun, Practice Tue 6 AM SPX 2); MMA A green Wed–Fri.",
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
  try:
    st=j(f'{s}_stats.json')
    ch=round((float(st['last'])-float(st['open']))/float(st['open'])*100,2) if 'open' in st and 'last' in st else 0.0
  except Exception:
    ch=0.0
  w.update(price=round(price,5) if price<1 else round(price,2), change24h=ch, asOf=NOW); crypto[s]=(price,ch)
b24=round((float(bst['last'])-float(bst['open']))/float(bst['open'])*100,2)
d['bitcoinDetail'].update(price=round(btc),change24h=b24,high24h=round(float(bst['high'])),low24h=round(float(bst['low'])),asOf=NOW)
d['meta'].update(lastUpdated=NOW,lastUpdatedLabel=NOWL,updatedBy="assistant-scheduled-refresh")
today=date(2026,10,31); ws=today-timedelta(days=(today.weekday()-5)%7)
if d.get('habitWeekStart')!=ws.isoformat():
  d['habitWeekStart']=ws.isoformat()
  for h in d['habits']: h['week']=[False]*7
w=j('weather_om.json'); dd=w['daily']; cur=w['current']
hi,lo=round(dd['temperature_2m_max'][0]),round(dd['temperature_2m_min'][0]); rain=dd['precipitation_probability_max'][0]
cC=round(cur['temperature_2m']); F=lambda c: round(c*9/5+32)
temp=dict(highC=hi,lowC=lo,highF=F(hi),lowF=F(lo),displayC=f"{hi}° / {lo}°C",displayF=f"{F(hi)}° / {F(lo)}°F",currentC=cC,currentF=F(cC))
wx=json.load(open('weather.json'))
wk=round(dd['wind_speed_10m_max'][0])
# Sunday-oriented: dry cool morning, dry through midweek, light rain chances later
pp=dd['precipitation_probability_max']
wx.update(date="2026-10-31",dateLabel="Sat Oct 31, 2026",
 conditions=f"Mostly cloudy and dry today: high ~{hi}°C / low ~{lo}°C, rain ~{rain}%, light wind (~{wk} km/h). Dry Sun–Tue (highs 11–13°C, lows ~3°C); showers return Wed–Fri (44–68%), breezier Thu–Fri.",
 conditionsShort="Cloudy, dry",temp=temp,rainChancePct=rain,
 wind=dict(summary="light",maxKmh=wk,display=f"Light, ~{wk} km/h"),
 sun=dict(sunrise=dd['sunrise'][0][-5:],sunset=dd['sunset'][0][-5:],sunriseLabel="7:56 AM",sunsetLabel="5:51 PM",timezoneNote="PT"),
 asOf=NOW,asOfLabel=NOWL,source="Open-Meteo (Langley BC)",lastUpdated=NOW)
json.dump(wx,open('weather.json','w'),indent=2,ensure_ascii=False)
d['weather'].update(conditionsShort=wx['conditionsShort'],temp=temp,rainChancePct=rain,asOf=NOW,asOfLabel=NOWL)
c=crypto
d['news']=[
 {"title":f"BTC ~${btc:,.0f} ({fmt(bp)} vs Fri snap; {fmt(b24)} 24h)","source":"Coinbase","date":"2026-10-31","dateLabel":"Oct 31","url":"https://www.coinbase.com/price/bitcoin"},
 {"title":f"Agent basket: NEAR ~${c['near'][0]:.3f} ({fmt(c['near'][1])} 24h); FET ~${c['fet'][0]:.4f} ({fmt(c['fet'][1])}); SOL ~${c['sol'][0]:.2f} ({fmt(c['sol'][1])}); ETH ~${c['eth'][0]:,.0f} ({fmt(c['eth'][1])})","source":"Coinbase","date":"2026-10-31","dateLabel":"Oct 31","url":"https://www.coinbase.com/price/near"},
 {"title":f"Gold ~${gold:,.0f} ({fmt(gp)}); WTI ~${wti:.2f} ({fmt(wp)} futures vs prior close); SPX {spx:,.2f} ({fmt(sp)} Fri close); US10Y {tnx:.2f}%","source":"gold-api / Yahoo","date":"2026-10-31","dateLabel":"Oct 31","url":"https://finance.yahoo.com/quote/%5EGSPC"},
 {"title":"TeamSnap posted U15 C4 Fallen Stars games in Mission: Fri Nov 6 6:15 PM, Sat Nov 7 9:15 AM and 1:45 PM (Fri vs C3 and Sat Development dropped). Tonight: U17 vs TBirds 5 PM Hillcrest.","source":"TeamSnap / LMHA","date":"2026-10-31","dateLabel":"Oct 31","url":"https://www.teamsnap.com/"},
]
json.dump(d,open('data.json','w'),indent=2,ensure_ascii=False)
mk=json.load(open('markets.json'))
mk['asOf']=NOW; mk['note']="Sat PT — gold gold-api; WTI futures Fri close; SPX/US10Y Fri close (Yahoo); BTC Coinbase"
mp={'gold':'xau','oil':'wti','btc':'btc','spx':'spx','us10y':'us10y'}
for s in mk['spots']:
  u=upd[mp[s['id']]]; s.update(value=u['value'],change=u['changeDisplay'],asOf="2026-10-31",status="live")
json.dump(mk,open('markets.json','w'),indent=2,ensure_ascii=False)
print(dict(btc=(btc,bp,b24),gold=(gold,gp),wti=(wti,wp),spx=(spx,sp),tnx=(tnx,tp),crypto=c,wx=(cC,hi,lo,rain,wk),habitWeek=d.get('habitWeekStart')))
