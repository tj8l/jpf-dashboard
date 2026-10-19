import json, re
from datetime import date, datetime, timedelta
NOW="2026-10-19T05:08:00-07:00"; NOWL="Mon Oct 19, 2026 · 5:08 AM PT"
cal=json.load(open('calendar.json'))
cal['fetchedAt']=NOW
# Align Google MMA A Nov/Dec shifts with Google's current representation
g={e['id']:e for e in json.load(open('tmp/gcal_events.json'))['events']}
for e in cal['events']:
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
 'ts-u17-10808348-375167688':('U17 Tournament #1 · vs Victoria Admirals',WIN,'arrive 10:00 AM, Maroon'),
 'ts-u17-10808348-375168061':('U17 HOLD · Team dinner (Kelowna)','Park Inn by Radisson (365 Mills Rd, Kelowna)','details to come'),
 'ts-u17-10808348-375167739':('U17 Tournament #2 · vs North Delta',WIN,'arrive 5:45 AM, White'),
 'ts-u17-10808348-375167827':('U17 Tournament #3 · vs New Westminster (U18 A1)',WIN,'arrive 3:45 PM, Maroon'),
 'ts-u17-10808348-375167894':('U17 HOLD · Semifinal (1st vs 4th)',WIN,'arrive 5:00 AM'),
 'ts-u17-10808348-375167921':('U17 HOLD · Semifinal (2nd vs 3rd)',WIN,'arrive 7:15 AM'),
 'ts-u17-10808348-375167954':('U17 HOLD · 5th/6th place game',WIN,'arrive 9:30 AM'),
 'ts-u17-10808348-375167995':('U17 HOLD · Gold Medal Game',WIN,'arrive 11:45 AM'),
 'ts-u17-10808348-375253591':('U17 Team Photo','George Preston Recreation Centre (Langley)','arrive noon, Maroon, full gear + stick, no skates/helmet/neck guard'),
}
for e in cal['events']:
  if e['id'] in fix:
    e['summary'],e['location'],extra=fix[e['id']]
    if extra not in e['whenLabel']: e['whenLabel']=e['whenLabel']+' ('+extra+')'
cal['range']=dict(start="2026-10-19",end="2026-10-25",label="Oct 19–25 (next 7 days)")
cal['notes']=[
 "Today Mon Oct 19: U17 League vs Vancouver TBirds 9:30–11:00 PM PT @ SPX 2. No U15 ice today. CLASH this week: Sat Oct 24 U15 C4 Development 10:45 AM @ LEC 3 sits between U17 Winfield games; Sun Oct 25 U15 C4 vs South Delta 7 PM @ LEC 2 after U17 Sunday holds in Lake Country.",
 "Week: Tue U15 C4 Practice 6:00 AM @ SPX 2; Wed 502 General Meeting 6–7 PM then U17 Development 7–8 PM @ LEC 2; Thu U17 Practice 9:15 PM @ SPX 2; Fri U17 Winfield opener 11:00 AM vs Victoria Admirals (Lake Country) + team dinner 5:45 PM Park Inn Kelowna; Sat Winfield #2 6:30 AM / #3 4:45 PM + U15 Development clash; Sun U17 holds through 2:45 PM, U15 C4 vs South Delta 7 PM LEC 2.",
 "U17 Winfield tournament (Lake Country/Kelowna) Oct 23–25 — Fri 11:00 AM vs Victoria Admirals; dinner 5:45 PM Park Inn Kelowna; Sat 6:30 AM vs North Delta and 4:45 PM vs New Westminster; Sun holds for semis/5th–6th/gold through 2:45 PM @ Winfield Arena.",
 "CLASH (next 7 days): Sat Oct 24 U15 C4 Development 10:45 AM @ LEC 3 between U17 Winfield games; Sun Oct 25 U15 C4 vs South Delta 7:00 PM @ LEC 2 after U17 holds that run to ~2:45 PM in Lake Country (~4 hr drive).",
 "Sun Nov 1: U17 Team Photo 12:00–12:30 PM @ George Preston Rec Centre (arrive noon, Maroon, full gear + stick, no skates/helmet/neck guard), U15 C4 Practice 1:20 PM same venue, U17 League vs Richmond 6:15 PM @ LEC 1.",
 "U15 C4 Mission tournament Fri Nov 6–Sun Nov 8 @ Mission Leisure Centre vs TBD (times TBD, arrive 12:00 PM). Clashes with U17 HOLD · Abbotsford Nov 6–9 and MMA A shifts Nov 6–8 (4 PM–12 AM).",
 "Weekly U17 Development Wednesdays 7:00–8:00 PM PT @ LEC 2 through Dec 16; Wed Oct 28 overlaps U15 C4 at Semiahmoo C4 (7:45 PM, Newton Arena); Wed Nov 4 during MMA A shift.",
 "MMA A block Nov 4–8 overlaps U17 Development Wed Nov 4 + Practice Thu Nov 5, Abbotsford HOLD Nov 6–9 and U15 C4 Mission Nov 6–8; MMA A block Dec 3–8 overlaps U17 Practice Dec 3 + Dec 7, Dryland Dec 4, League vs North Vancouver Sat Dec 5 4:45 PM, and HOLD LEC 1 Dec 6.",
 "Mon Nov 16 U17 League vs South Delta 9:00 PM overlaps U17 Practice 9:30 PM @ SPX 2 (TeamSnap — likely practice replaced by game).",
 "Weekbar Mon Oct 19–Sun Oct 25: U17 yellow (League Mon TBirds SPX 2 9:30 PM, Development Wed 7 PM LEC 2, Practice Thu 9:15 PM SPX 2, Winfield Fri–Sun); U15 orange (Practice Tue 6 AM SPX 2, Development Sat 10:45 AM LEC 3, vs South Delta Sun 7 PM LEC 2). Wed Oct 21 502 General Meeting 6–7 PM.",
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
today=date(2026,10,19); ws=today-timedelta(days=(today.weekday()-5)%7)
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
rain_fri=dd['precipitation_probability_max'][5]
rain_sat=dd['precipitation_probability_max'][6]
wx.update(date="2026-10-19",dateLabel="Mon Oct 19, 2026",
 conditions=f"Cool start (~{cC}°C now), mostly cloudy; dry today (rain ~{rain}%), high ~{hi}°C / low ~{lo}°C, light winds. Tue–Wed dry and mild (Tue high ~20°C); Thu–Fri slight rain chances (~10–12%); Sat–Sun showers possible (~{dd['precipitation_probability_max'][5]}–{dd['precipitation_probability_max'][6]}%), highs ~14°C.",
 conditionsShort="Cloudy, dry",temp=temp,rainChancePct=rain,
 wind=dict(summary="light",maxKmh=wk,display=f"Light, ~{wk} km/h"),
 sun=dict(sunrise=dd['sunrise'][0][-5:],sunset=dd['sunset'][0][-5:],sunriseLabel="7:37 AM",sunsetLabel="6:12 PM",timezoneNote="PT"),
 asOf=NOW,asOfLabel=NOWL,source="Open-Meteo (Langley BC)",lastUpdated=NOW)
json.dump(wx,open('weather.json','w'),indent=2,ensure_ascii=False)
d['weather'].update(conditionsShort=wx['conditionsShort'],temp=temp,rainChancePct=rain,asOf=NOW,asOfLabel=NOWL)
c=crypto
d['news']=[
 {"title":f"BTC ~${btc:,.0f} ({fmt(bp)} vs Sun snap; {fmt(b24)} 24h)","source":"Coinbase","date":"2026-10-19","dateLabel":"Oct 19","url":"https://www.coinbase.com/price/bitcoin"},
 {"title":f"Agent basket: NEAR ~${c['near'][0]:.3f} ({fmt(c['near'][1])} 24h); FET ~${c['fet'][0]:.4f} ({fmt(c['fet'][1])}); SOL ~${c['sol'][0]:.2f} ({fmt(c['sol'][1])}); ETH ~${c['eth'][0]:,.0f} ({fmt(c['eth'][1])})","source":"Coinbase","date":"2026-10-19","dateLabel":"Oct 19","url":"https://www.coinbase.com/price/near"},
 {"title":f"Gold ~${gold:,.0f} ({fmt(gp)}); WTI ~${wti:.2f} ({fmt(wp)}); SPX {spx:,.2f} ({fmt(sp)} Fri close); US10Y {tnx:.2f}%","source":"gold-api / Yahoo","date":"2026-10-19","dateLabel":"Oct 19","url":"https://finance.yahoo.com/quote/%5EGSPC"},
 {"title":"Tonight: U17 League vs Vancouver TBirds SPX 2 9:30 PM. Sat clash: U15 Development during Winfield; Sun U15 vs South Delta 7 PM after Winfield holds","source":"TeamSnap / LMHA","date":"2026-10-19","dateLabel":"Oct 19","url":"https://www.teamsnap.com/"},
]
json.dump(d,open('data.json','w'),indent=2,ensure_ascii=False)
mk=json.load(open('markets.json'))
mk['asOf']=NOW; mk['note']="Mon pre-open PT — gold gold-api; WTI/SPX/US10Y Yahoo (Fri close vs prior close); BTC Coinbase"
mp={'gold':'xau','oil':'wti','btc':'btc','spx':'spx','us10y':'us10y'}
for s in mk['spots']:
  u=upd[mp[s['id']]]; s.update(value=u['value'],change=u['changeDisplay'],asOf="2026-10-19",status="live")
json.dump(mk,open('markets.json','w'),indent=2,ensure_ascii=False)
print(dict(btc=(btc,bp,b24),gold=(gold,gp),wti=(wti,wp),spx=(spx,sp),tnx=(tnx,tp),crypto=c,wx=(cC,hi,lo,rain,wk),habitWeek=d.get('habitWeekStart')))
