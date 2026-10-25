import json, re
from datetime import date, datetime, timedelta
NOW="2026-10-25T05:15:00-07:00"; NOWL="Sun Oct 25, 2026 · 5:15 AM PT"
cal=json.load(open('calendar.json'))
cal['fetchedAt']=NOW
# Align Google MMA A Nov/Dec shifts with Google's current representation
g={e['id']:e for e in json.load(open('tmp/gcal_events.json'))['events']}
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
 'ts-u17-10808348-375253591':('U17 Team Photo','George Preston Recreation Centre (Langley)','arrive noon, Maroon, full gear + stick, no skates/helmet/neck guard'),
}
for e in cal['events']:
  if e['id']=='ts-u17-10808348-375563260':
    e['start']='2026-10-25T06:00:00-07:00'; e['end']='2026-10-25T08:00:00-07:00'
for e in cal['events']:
  if e['id'] in fix:
    e['summary'],e['location'],extra=fix[e['id']]
    if extra not in e['whenLabel']: e['whenLabel']=e['whenLabel']+' ('+extra+')'
cal['range']=dict(start="2026-10-25",end="2026-10-31",label="Oct 25–31 (next 7 days)")
for e in cal['events']:
  if e['id']=='ts-u15-10816643-375390752':
    e['summary']='U15 C4 Practice · George Preston Rec Centre'
    e['location']='George Preston Recreation Centre (20699 42 Ave, Langley)'
    if 'arrive 10:45' not in e['whenLabel']: e['whenLabel']=e['whenLabel']+' (arrive 10:45 AM; overlaps U17 Team Photo 12:00 same venue)'
# Abbotsford tournament: TeamSnap entered these with TZID America/Vancouver; keep typed wall times on the board's Pacific convention
ab={
 'ts-u17-10808348-375456255':('U17 Abbotsford #1 · vs Penticton U18 A2','Matsqui Recreation Centre (3106 Clearbrook Rd, Abbotsford)','2026-11-06T14:45:00-08:00','2026-11-06T16:45:00-08:00','Fri Nov 6 · 2:45 PM–4:45 PM PT (arrive 1:45 PM, White — bring both)'),
 'ts-u17-10808348-375456336':('U17 Abbotsford #2 · vs Squamish U18 A2','MSA Arena (2323 Emerson St, Abbotsford)','2026-11-07T10:15:00-08:00','2026-11-07T12:15:00-08:00','Sat Nov 7 · 10:15 AM–12:15 PM PT (arrive 9:15 AM, Maroon — bring both)'),
 'ts-u17-10808348-375456404':('U17 Abbotsford #3 · vs West Kelowna U18 A2','Summit Centre – West (3600 Townline Rd, Abbotsford)','2026-11-08T07:15:00-08:00','2026-11-08T09:15:00-08:00','Sun Nov 8 · 7:15 AM–9:15 AM PT (arrive 6:15 AM, White — bring both)'),
}
for e in cal['events']:
  if e['id'] in ab: e['summary'],e['location'],e['start'],e['end'],e['whenLabel']=ab[e['id']]
if not any(e['id']=='7vco3epcilqssjvuctejjun98g' for e in cal['events']):
  cal['events'].append(dict(id='7vco3epcilqssjvuctejjun98g',summary='Zoom call with Bruce (Your Life Is the Ceremony)',location='Zoom / Skool',start='2026-11-04T16:00:00-08:00',end='2026-11-04T17:00:00-08:00',whenLabel='Wed Nov 4 · 4:00 PM–5:00 PM PT'))
cal['events'].sort(key=lambda e:e['start'])
cal['notes']=[
 "Today Sun Oct 25: U17 Winfield vs TriCity U18 A2 6:00 AM (arrive 5:15, Maroon — semifinal slot) and Gold Medal HOLD 12:45 PM in Lake Country; U15 C4 vs South Delta C1 7:00 PM @ LEC 2 (arrive 6:15). U15 C4 vs Cloverdale (was Fri Oct 23) remains POSTPONED.",
 "Week: Mon U17 Practice 9:30 PM SPX 2; Tue U15 C4 Practice 6 AM SPX 2; Wed Oct 28 U17 Development 7 PM LEC 2 overlaps U15 C4 at Semiahmoo C4 7:45 PM Newton Arena; Thu U17 Practice 9:15 PM SPX 2; Fri U17 Dryland 8:30 PM Aim Athletic; Sat Oct 31 U17 League vs Vancouver TBirds 5 PM Hillcrest.",
 "NEW from TeamSnap (U15 C4 Nov schedule): Sun Nov 1 at C1 7 PM LEC 2; Tue practices 6 AM SPX 2 Nov 3/10/17; Fri Nov 6 vs C3 7 PM LEC 2; Sat Nov 7 + Nov 21 Development with C1 10:45 AM LEC 3; Fri Nov 13 vs C2 7 PM LEC 2; Sun Nov 15 + Nov 22 vs C3 7 PM LEC 2.",
 "New U15 clashes: Sun Nov 1 U15 at C1 7 PM LEC 2 overlaps U17 League vs Richmond 6:15 PM LEC 1 (same building); Sun Nov 15 and Nov 22 U15 7 PM LEC 2 overlap U17 League 6:15 PM LEC 1; Fri Nov 13 U15 vs C2 7–8:30 PM runs into U17 Dryland 8:30 PM.",
 "Nov 6–8 pileup: Fri Nov 6 U15 vs C3 7 PM LEC 2 + U15 Mission tournament + U17 Abbotsford vs Penticton 2:45 PM + MMA A 4 PM–12 AM; Sat Nov 7 U15 Development 10:45 AM LEC 3 vs U17 Abbotsford vs Squamish 10:15 AM + Mission + MMA A; Sun Nov 8 U17 vs West Kelowna 7:15 AM + Mission + MMA A.",
 "Google Calendar also has U15 items TeamSnap doesn't yet: C3/C4 game slots (TBD) Sun Nov 8 and Nov 29 7 PM LEC 2, practices Tue Nov 24 and Dec 1 6 AM SPX 2 — not on the board until TeamSnap posts them.",
 "U17 Abbotsford tournament Nov 6–8 — Fri 2:45 PM vs Penticton U18 A2 @ Matsqui Rec (arrive 1:45, White); Sat 10:15 AM vs Squamish U18 A2 @ MSA Arena (arrive 9:15, Maroon); Sun 7:15 AM vs West Kelowna U18 A2 @ Summit Centre West (arrive 6:15, White).",
 "Zoom call with Bruce Wed Nov 4 4–5 PM PT — overlaps MMA A shift (4 PM–12 AM) and comes before U17 Development 7 PM.",
 "Sun Nov 1: U15 C4 Practice 11:15 AM–12:45 PM, U17 Team Photo 12:00–12:30 PM (arrive noon, Maroon, full gear + stick, no skates/helmet/neck guard), U15 C4 Team Photo 1:20 PM — all George Preston Rec Centre; U17 League vs Richmond 6:15 PM @ LEC 1; U15 at C1 7 PM @ LEC 2.",
 "Weekly U17 Development Wednesdays 7:00–8:00 PM PT @ LEC 2 through Dec 16; Wed Nov 4 during MMA A shift.",
 "MMA A block Dec 3–8 overlaps U17 Practice Dec 3 + Dec 7, Dryland Dec 4, League vs North Vancouver Sat Dec 5 4:45 PM, and HOLD LEC 1 Dec 6.",
 "Mon Nov 16 U17 League vs South Delta 9:00 PM overlaps U17 Practice 9:30 PM @ SPX 2 (TeamSnap — likely practice replaced by game).",
 "Weekbar Sun Oct 25–Sat Oct 31: U15 orange (vs South Delta Sun 7 PM LEC 2, Practice Tue 6 AM SPX 2, at Semiahmoo Wed 7:45 PM); U17 yellow (Winfield Sun, Practice Mon + Thu SPX 2, Development Wed 7 PM, Dryland Fri 8:30 PM, vs TBirds Sat 5 PM).",
 "No MMA shifts on Google Calendar until Wed Nov 4.",
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
today=date(2026,10,25); ws=today-timedelta(days=(today.weekday()-5)%7)
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
wx.update(date="2026-10-25",dateLabel="Sun Oct 25, 2026",
 conditions=f"Rain today: high ~{hi}°C / low ~{lo}°C, rain ~{rain}%, breezy (~{round(dd['wind_speed_10m_max'][0])} km/h). Mon mostly dry; wet again Tue–Thu (highs 10–11°C); drier and colder Fri–Sat (lows near 1°C).",
 conditionsShort="Rain, mild",temp=temp,rainChancePct=rain,
 wind=dict(summary="breezy",maxKmh=wk,display=f"Breezy, ~{wk} km/h"),
 sun=dict(sunrise=dd['sunrise'][0][-5:],sunset=dd['sunset'][0][-5:],sunriseLabel="7:47 AM",sunsetLabel="6:01 PM",timezoneNote="PT"),
 asOf=NOW,asOfLabel=NOWL,source="Open-Meteo (Langley BC)",lastUpdated=NOW)
json.dump(wx,open('weather.json','w'),indent=2,ensure_ascii=False)
d['weather'].update(conditionsShort=wx['conditionsShort'],temp=temp,rainChancePct=rain,asOf=NOW,asOfLabel=NOWL)
c=crypto
d['news']=[
 {"title":f"BTC ~${btc:,.0f} ({fmt(bp)} vs Sat snap; {fmt(b24)} 24h)","source":"Coinbase","date":"2026-10-25","dateLabel":"Oct 25","url":"https://www.coinbase.com/price/bitcoin"},
 {"title":f"Agent basket: NEAR ~${c['near'][0]:.3f} ({fmt(c['near'][1])} 24h); FET ~${c['fet'][0]:.4f} ({fmt(c['fet'][1])}); SOL ~${c['sol'][0]:.2f} ({fmt(c['sol'][1])}); ETH ~${c['eth'][0]:,.0f} ({fmt(c['eth'][1])})","source":"Coinbase","date":"2026-10-25","dateLabel":"Oct 25","url":"https://www.coinbase.com/price/near"},
 {"title":f"Gold ~${gold:,.0f} ({fmt(gp)}); WTI ~${wti:.2f} ({fmt(wp)} vs prior close); SPX {spx:,.2f} ({fmt(sp)} Fri close); US10Y {tnx:.2f}%","source":"gold-api / Yahoo","date":"2026-10-25","dateLabel":"Oct 25","url":"https://finance.yahoo.com/quote/%5EGSPC"},
 {"title":"TeamSnap posted the U15 C4 November schedule (9 new events: games Nov 1, 6, 13, 15, 22; Tue 6 AM practices; Sat Development with C1). Today: U17 Winfield vs TriCity 6 AM; U15 C4 vs South Delta 7 PM LEC 2.","source":"TeamSnap / LMHA","date":"2026-10-25","dateLabel":"Oct 25","url":"https://www.teamsnap.com/"},
]
json.dump(d,open('data.json','w'),indent=2,ensure_ascii=False)
mk=json.load(open('markets.json'))
mk['asOf']=NOW; mk['note']="Sun PT — gold gold-api; WTI/SPX/US10Y Fri close vs prior close (Yahoo); BTC Coinbase"
mp={'gold':'xau','oil':'wti','btc':'btc','spx':'spx','us10y':'us10y'}
for s in mk['spots']:
  u=upd[mp[s['id']]]; s.update(value=u['value'],change=u['changeDisplay'],asOf="2026-10-25",status="live")
json.dump(mk,open('markets.json','w'),indent=2,ensure_ascii=False)
print(dict(btc=(btc,bp,b24),gold=(gold,gp),wti=(wti,wp),spx=(spx,sp),tnx=(tnx,tp),crypto=c,wx=(cC,hi,lo,rain,wk),habitWeek=d.get('habitWeekStart')))
