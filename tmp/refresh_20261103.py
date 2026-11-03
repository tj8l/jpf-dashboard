import json
from datetime import date, timedelta
NOW="2026-11-03T05:10:00-08:00"; NOWL="Tue Nov 3, 2026 · 5:10 AM PT"
cal=json.load(open('calendar.json'))
cal['fetchedAt']=NOW
cal['events'].sort(key=lambda e:e['start'])
cal['range']=dict(start="2026-11-03",end="2026-11-09",label="Nov 3–9 (next 7 days)")
cal['notes']=[
 "Today Tue Nov 3: U15 C4 Practice 6:00 AM @ SPX 2. Cloudy and dry, 14°/5°C; rain arrives Wed and sticks around through Sun.",
 "TeamSnap change: U15 C4's opponent C3 is now listed as LANGLEY C3 – Havoc (Sun Nov 15 + Nov 22, 7 PM LEC 2); times and rinks unchanged.",
 "Week: Wed Nov 4 MMA A 4 PM + Zoom with Bruce 4 PM + U17 Development 7 PM LEC 2; Thu Nov 5 MMA A 4 PM + U17 Practice 9:15 PM SPX 2; Fri Nov 6 Dentist 9:20 AM Fort Langley Dental.",
 "Nov 6–8 pileup: Fri Nov 6 U17 Abbotsford vs Penticton 2:45 PM (Matsqui, arrive 1:45, White) + MMA A 4 PM–12 AM + U15 Mission vs TBirds 6:15 PM; Sat Nov 7 U15 Mission 9:15 AM + U17 vs Squamish 10:15 AM (MSA) + U15 Mission 1:45 PM + MMA A 4 PM; Sun Nov 8 U17 vs West Kelowna 9:00 AM (Summit West) + U15 Mission TBD (arrive noon) + MMA A 4 PM.",
 "Mon Nov 9: U17 Abbotsford playoff day 7:45 AM–7:45 PM (Matsqui; semis 12:15–2:15 MRC/Summit West; gold 5–7 PM MSA), then U17 Practice 9:30 PM SPX 2.",
 "U15 C4 November (TeamSnap): Tue practices 6 AM SPX 2 Nov 3/10/17; Fri Nov 13 vs Pink Pigeons (C2) 7 PM LEC 2; Sun Nov 15 + Nov 22 vs C3 Havoc 7 PM LEC 2; Sat Nov 21 Development with C1 10:45 AM LEC 3.",
 "Clashes: Sun Nov 15 and Nov 22 U15 7 PM LEC 2 overlap U17 League 6:15 PM LEC 1; Fri Nov 13 U15 7–8:30 PM runs into U17 Dryland 8:30 PM; Thu Nov 5 U17 Practice 9:15 PM during MMA A shift; Wed Nov 4 Zoom with Bruce overlaps MMA A.",
 "Google Calendar still has stale U15 items TeamSnap dropped or hasn't posted (Fri Nov 6 vs C3, Sat Nov 7 Development, C3/C4 slots Nov 8/29, practices Nov 24 and Dec 1), and its Fallen Stars and practice entries read one hour early — TeamSnap times are on the board.",
 "Abbotsford Winter Extreme Ski & Board Sale, Sat–Sun Nov 14–15, Ag-Rec Centre (hours not posted).",
 "Weekly U17 Development Wednesdays 7:00–8:00 PM PT @ LEC 2 through Dec 16 (no session Nov 11).",
 "MMA A block Dec 3–8 overlaps U17 Practice Dec 3 + Dec 7, Dryland Dec 4, League vs North Vancouver Sat Dec 5 4:45 PM, and HOLD LEC 1 Dec 6.",
 "Mon Nov 16 U17 League vs South Delta 9:00 PM overlaps U17 Practice 9:30 PM @ SPX 2 (TeamSnap — likely practice replaced by game).",
 "Weekbar Tue Nov 3–Mon Nov 9: U15 orange Tue; MMA A green Wed–Sun (U17/U15 tournament games Fri–Sun); U17 yellow Mon.",
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
today=date(2026,11,3); ws=today-timedelta(days=(today.weekday()-5)%7)
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
wx.update(date="2026-11-03",dateLabel="Tue Nov 3, 2026",
 conditions=f"Overcast and dry: high ~{hi}°C / low ~{lo}°C, rain ~{rain}%, light wind (~{wk} km/h). Rain Wed–Thu (95%) and showers Fri–Sun (82–83%), windy Sun; cold dry start Mon (low ~2°C).",
 conditionsShort="Cloudy, dry",temp=temp,rainChancePct=rain,
 wind=dict(summary="light",maxKmh=wk,display=f"Light, ~{wk} km/h"),
 sun=dict(sunrise=dd['sunrise'][0][-5:],sunset=dd['sunset'][0][-5:],sunriseLabel="7:01 AM",sunsetLabel="4:46 PM",timezoneNote="PT"),
 asOf=NOW,asOfLabel=NOWL,source="Open-Meteo (Langley BC)",lastUpdated=NOW)
json.dump(wx,open('weather.json','w'),indent=2,ensure_ascii=False)
d['weather'].update(conditionsShort=wx['conditionsShort'],temp=temp,rainChancePct=rain,asOf=NOW,asOfLabel=NOWL)
c=crypto
d['news']=[
 {"title":f"BTC ~${btc:,.0f} ({fmt(bp)} vs Mon snap; {fmt(b24)} 24h)","source":"Coinbase","date":"2026-11-03","dateLabel":"Nov 3","url":"https://www.coinbase.com/price/bitcoin"},
 {"title":f"Agent basket: NEAR ~${c['near'][0]:.3f} ({fmt(c['near'][1])} 24h); FET ~${c['fet'][0]:.4f} ({fmt(c['fet'][1])}); SOL ~${c['sol'][0]:.2f} ({fmt(c['sol'][1])}); ETH ~${c['eth'][0]:,.0f} ({fmt(c['eth'][1])})","source":"Coinbase","date":"2026-11-03","dateLabel":"Nov 3","url":"https://www.coinbase.com/price/near"},
 {"title":f"Gold ~${gold:,.0f} ({fmt(gp)}); WTI ~${wti:.2f} ({fmt(wp)} futures vs prior close); SPX {spx:,.2f} ({fmt(sp)} Mon close); US10Y {tnx:.2f}%","source":"gold-api / Yahoo","date":"2026-11-03","dateLabel":"Nov 3","url":"https://finance.yahoo.com/quote/%5EGSPC"},
 {"title":"Today: U15 C4 practice 6 AM at SPX 2. TeamSnap now lists U15 C4's C3 opponent as C3 Havoc (Nov 15 + 22). Big weekend: U17 Abbotsford tournament + U15 Fallen Stars in Mission Nov 6–8.","source":"TeamSnap / LMHA","date":"2026-11-03","dateLabel":"Nov 3","url":"https://www.teamsnap.com/"},
]
json.dump(d,open('data.json','w'),indent=2,ensure_ascii=False)
mk=json.load(open('markets.json'))
mk['asOf']=NOW; mk['note']="Tue pre-open PT — gold gold-api; WTI futures live vs Mon close; SPX/US10Y Mon close (Yahoo); BTC Coinbase"
mp={'gold':'xau','oil':'wti','btc':'btc','spx':'spx','us10y':'us10y'}
for s in mk['spots']:
  u=upd[mp[s['id']]]; s.update(value=u['value'],change=u['changeDisplay'],asOf="2026-11-03",status="live")
json.dump(mk,open('markets.json','w'),indent=2,ensure_ascii=False)
print(dict(btc=(btc,bp,b24),gold=(gold,gp),wti=(wti,wp),spx=(spx,sp),tnx=(tnx,tp),crypto=c,wx=(cC,hi,lo,rain,wk),habitWeek=d.get('habitWeekStart')))
