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
t=date(2026,10,23); rows=[]
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
banner='<div class="today-banner">Today · Friday — U17 Winfield opener 11 AM vs Victoria Admirals, then 5:45 PM dinner + parent meeting in Kelowna. U15 C4 vs Cloverdale stays POSTPONED. Sat U15 Development 10:45 AM LEC 3 between Winfield games; Sun U15 C4 vs South Delta 7 PM LEC 2 after Winfield holds. Sunny and dry, 15°/3°C; showers Sat–Sun.</div>'
html,n2=re.subn(r'<div class="today-banner">.*?</div>',lambda m:banner,html,count=1,flags=re.S)
key='window.__JPF_BAKED__ = '
i=html.index(key)+len(key)
obj,end=json.JSONDecoder().raw_decode(html,i)
baked={f:json.load(open(f)) for f in ['calendar.json','data.json','markets.json','weather.json','teamsnap.json']}
html=html[:i]+json.dumps(baked,ensure_ascii=False)+html[end:]
open('index.html','w',encoding='utf-8').write(html)
print('weekbar',n1,'banner',n2,'baked keys',list(baked))
