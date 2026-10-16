import json, re
from datetime import date, timedelta, datetime
html=open('index.html',encoding='utf-8').read()
cal=json.load(open('calendar.json'))
def cls(s):
  s=re.sub(r'[·•–—]',' ',s.lower()); s=re.sub(r'\s+',' ',s)
  if re.search(r'\bmma\s*d\b',s): return 'cal-dayshift'
  if re.search(r'\bmma\s*a\b',s): return 'cal-afternoon'
  if re.search(r'\bmma\s*n\b',s): return 'cal-graveyard'
  if 'u15' in s: return 'cal-u15'
  if 'u17' in s: return 'cal-u17'
  if 'u18' in s: return 'cal-u18'
  return 'cal-other'
rank={'cal-dayshift':1,'cal-afternoon':2,'cal-graveyard':3,'cal-u15':4,'cal-u17':5,'cal-u18':6,'cal-other':9}
t=date(2026,10,16); rows=[]
for i in range(7):
  d=t+timedelta(days=i); ymd=d.isoformat()
  evs=[e for e in cal['events'] if e['start'][:10]==ymd]
  for e in evs: print(ymd,e['summary'],e['start'][11:16])
  c='dow'+(' today' if i==0 else '')+(' has' if evs else '')
  if evs:
    if any('draft' in e['summary'].lower() for e in evs): best='cal-u15'
    else: best=min((cls(e['summary']) for e in evs),key=lambda k:rank[k])
    c+=' '+best
  rows.append(f'          <div class="{c}" data-date="{ymd}"><span class="k">{d.strftime("%a")}</span><span class="d">{d.day}</span><span class="dot"></span></div>')
new='<div class="weekbar" id="weekbar" aria-label="Next 7 days">\n'+'\n'.join(rows)+'\n        </div>'
html,n1=re.subn(r'<div class="weekbar" id="weekbar" aria-label="Next 7 days">.*?\n        </div>',lambda m:new,html,count=1,flags=re.S)
banner='<div class="today-banner">Today · Friday — U17 League vs Cloverdale 8:45 PM @ Cloverdale. Sat U15 C4 at Cloverdale C3 5:30 PM; Sun U17 League vs South Delta LEC 1 6:15 PM; Mon U17 League vs Vancouver TBirds SPX 2 9:30 PM; Tue U15 C4 practice SPX 2 6 AM; Wed 502 General Meeting 6 PM + U17 Development LEC 2 7 PM; Thu U17 Practice SPX 2 9:15 PM. No clashes this week. Winfield tournament Oct 23–25 still on the board (Sat Oct 24 clash with U15 Development). Dry, 22°/6°C.</div>'
html,n2=re.subn(r'<div class="today-banner">.*?</div>',lambda m:banner,html,count=1,flags=re.S)
key='window.__JPF_BAKED__ = '
i=html.index(key)+len(key)
obj,end=json.JSONDecoder().raw_decode(html,i)
baked={f:json.load(open(f)) for f in ['calendar.json','data.json','markets.json','weather.json','teamsnap.json']}
html=html[:i]+json.dumps(baked,ensure_ascii=False)+html[end:]
open('index.html','w',encoding='utf-8').write(html)
print('weekbar',n1,'banner',n2,'baked keys',list(baked))
