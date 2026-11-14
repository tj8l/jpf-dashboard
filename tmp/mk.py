
import re
s=open('tmp/refresh_20261113.py').read()
a=s.index("# Restore hand"); b=s.index("json.dump(cal")
new='''cal['events'].sort(key=lambda e:e['start'])
cal['range']=dict(start="2026-11-14",end="2026-11-20",label="Nov 14–20 (next 7 days)")
cal['notes']=[
 "Today Sat Nov 14: U15 C4 at Semiahmoo C3 8:00 PM, South Surrey Arena (arrive 7:15). Sun Nov 15: U17 League vs Cloverdale 6:15 PM LEC 1 + U15 vs C3 7 PM LEC 2. Mon Nov 16: U17 League vs South Delta 7:30 PM. Tue Nov 17: U15 C4 Practice 6 AM SPX 2. Wed Nov 18: U17 Development 7 PM LEC 2. Thu Nov 19: U17 Practice 9:15 PM SPX 2. Fri Nov 20: U17 Dryland 8:30 PM.",
 "TeamSnap overnight: no schedule changes (Fri Nov 13 items aged out; Sun Nov 15 and Nov 22 opponent shown as C3).",
 "Clashes: Sun Nov 15 and Nov 22 U15 7 PM LEC 2 overlap U17 League 6:15 PM LEC 1.",
 "Google Calendar unchanged (stale U15 items TeamSnap dropped or replaced, and TBD slot, stay excluded).",
 "Abbotsford Winter Extreme Ski & Board Sale, Sat-Sun Nov 14-15, Ag-Rec Centre (hours not posted).",
 "MMA A block Dec 3-8 overlaps U17 Practice Dec 3 + Dec 7, Dryland Dec 4, League vs North Vancouver Sat Dec 5 4:45 PM, and HOLD LEC 1 Dec 6.",
 "TeamSnap LANGLEY MHA U17 A1 + U15 C4 are source of truth for both teams' ice through Mar 20, 2027; MMA, personal, and PCAHA meetings preserved."
]
'''
s=s[:a]+new+s[b:]
s=s.replace('2026-11-13T05:10:00-08:00','2026-11-14T05:10:00-08:00').replace('Fri Nov 13, 2026 · ~5:10','Sat Nov 14, 2026 · ~5:10').replace('date(2026,11,13)','date(2026,11,14)').replace('2026-11-13','2026-11-14').replace('Fri Nov 13, 2026','Sat Nov 14, 2026')
s=s.replace('Friday: high','Saturday: high')
s=re.sub(r'conditions=f"[^\n]*\n','conditions=f"Saturday: high ~{hi}°C / low ~{lo}°C, rain ~{rain}%, wind ~{wk} km/h. Sun (~{pp[1]}%), Mon (~{pp[2]}%).",\n',s,count=1)
s=s.replace("Today: U15 vs Pink Pigeons 7 PM LEC 2, U17 Dryland 8:30 PM.","Today: U15 C4 at Semiahmoo C3 8 PM (arrive 7:15).")
open('tmp/refresh_20261114.py','w').write(s)
t=open('tmp/bake_20261113.py').read().replace('date(2026,11,13)','date(2026,11,14)')
t=t.replace("Today · Friday — U15 vs Pink Pigeons 7 PM LEC 2, U17 Dryland 8:30 PM.","Today · Saturday — U15 C4 at Semiahmoo C3 8 PM South Surrey Arena (arrive 7:15).")
open('tmp/bake_20261114.py','w').write(t)
