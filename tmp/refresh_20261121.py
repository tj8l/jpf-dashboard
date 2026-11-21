#!/usr/bin/env python3
"""Daily Command Center refresh for 2026-11-21."""
import json
import re
from datetime import datetime, date, timedelta

ASOF = "2026-11-21T05:00:00-07:00"
ASOF_LABEL = "Sat Nov 21, 2026 · ~5:00 AM PT"
TODAY = date(2026, 11, 21)


def half_up(x):
    return int(x + 0.5) if x >= 0 else int(x - 0.5)


def c_to_f(c):
    return half_up(c * 9 / 5 + 32)


def pct(new, old):
    return (new - old) / old * 100


def money(n, decimals=0):
    if decimals == 0:
        return f"${n:,.0f}"
    return f"${n:,.{decimals}f}"


def fmt_time(dt: datetime) -> str:
    h, m = dt.hour, dt.minute
    ampm = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {ampm}"


def when_label(start: str, end: str) -> str:
    s = datetime.fromisoformat(start)
    e = datetime.fromisoformat(end)
    return f"{s.strftime('%a %b')} {s.day} · {fmt_time(s)}–{fmt_time(e)} PT"


def short_loc(loc: str, summary: str) -> str:
    loc = loc or ""
    if "Aldergrove" in loc or "Aldergrove" in summary:
        return "Aldergrove Community Centre"
    if "Langley Events Centre" in loc or "LEC" in summary or "ARENAS" in loc:
        return "LEC Arena 3 (Burgundy)"
    return loc


# --- merge Google personal stick & puck (TeamSnap remains SoT for U15/U17 ice) ---
cal = json.load(open("calendar.json"))
gcal = json.load(open("tmp/gcal_events_20261121.json"))
existing_ids = {e["id"] for e in cal["events"]}
added_stick = []
for ev in gcal["events"]:
    summary = ev.get("summary") or ""
    if "stick & puck" not in summary.lower():
        continue
    eid = ev["id"]
    if eid in existing_ids:
        continue
    start = ev["start"]["dateTime"]
    end = ev["end"]["dateTime"]
    # Trust returned -07:00 wall clocks for these series (instance UTC matches 4:00/4:30/5:45 PM UTC-7).
    item = {
        "id": eid,
        "summary": summary,
        "location": short_loc(ev.get("location") or "", summary),
        "start": start,
        "end": end,
        "whenLabel": when_label(start, end),
    }
    if ev.get("description"):
        item["description"] = ev["description"]
    cal["events"].append(item)
    added_stick.append(item)
    existing_ids.add(eid)

cal["events"].sort(key=lambda e: (e.get("start") or "", e.get("id") or ""))

# Refresh 7-day notes (preserve MMA/Kevin; do not touch TeamSnap titles)
def evs_on(ymd):
    return [e for e in cal["events"] if (e.get("start") or "")[:10] == ymd]

week_notes = []
for i in range(7):
    d = TODAY + timedelta(days=i)
    evs = evs_on(d.isoformat())
    if not evs:
        continue
    bits = []
    for e in evs:
        t = datetime.fromisoformat(e["start"])
        loc = e.get("location") or ""
        loc_bit = f" @ {loc}" if loc else ""
        bits.append(f"{e['summary']} {fmt_time(t)}{loc_bit}")
    label = "Today Sat Nov 21" if i == 0 else d.strftime("%a %b ") + str(d.day)
    week_notes.append(f"{label}: " + "; ".join(bits) + ".")

beyond = []
for e in cal["events"]:
    ds = (e.get("start") or "")[:10]
    if "2026-11-28" <= ds <= "2026-12-02":
        beyond.append(e)
beyond_by = {}
for e in beyond:
    ds = e["start"][:10]
    beyond_by.setdefault(ds, []).append(e["summary"].split(" · ")[0])
if beyond_by:
    parts = []
    for ds, titles in beyond_by.items():
        d = date.fromisoformat(ds)
        uniq = []
        for t in titles:
            if t not in uniq:
                uniq.append(t)
        parts.append(f"{d.strftime('%a %b')} {d.day} ({', '.join(uniq)})")
    week_notes.append(
        "Beyond 7-day day-list window: " + "; ".join(parts) + " — still in calendar.json events."
    )
week_notes.append(
    "TeamSnap LANGLEY MHA U17 A1 + U15 C4 is source of truth for both teams' ice; "
    "Amanda/Google U17 and Google U15 C/C4 ice replaced. MMA, personal, and PCAHA meetings preserved. "
    "PCAHA dates from 2026–2027 Bulletin #5. Stick & puck (Barrett) added from Google Calendar primary; "
    "MMA A wall times kept at 4:00 PM–12:00 AM PT (spreadsheet / existing board; Google America/Vancouver still renders one hour late)."
)
cal["notes"] = week_notes
cal["fetchedAt"] = ASOF
cal["range"] = {
    "start": "2026-11-21",
    "end": "2026-11-27",
    "label": "Nov 21–27 (next 7 days)",
}
json.dump(cal, open("calendar.json", "w"), indent=2, ensure_ascii=False)
open("calendar.json", "a").write("\n")
print(f"calendar events={len(cal['events'])} stick_added={len(added_stick)}")

# --- weather ---
wx_raw = json.load(open("tmp/weather_om.json"))
sun_raw = json.load(open("tmp/weather_sun.json"))
hi_c = half_up(wx_raw["daily"]["temperature_2m_max"][0])
lo_c = half_up(wx_raw["daily"]["temperature_2m_min"][0])
cur_c = half_up(wx_raw["current"]["temperature_2m"])
rain = int(wx_raw["daily"]["precipitation_probability_max"][0])
wind = half_up(wx_raw["daily"]["wind_speed_10m_max"][0])
sat_r = rain
sun_r = int(wx_raw["daily"]["precipitation_probability_max"][1])
mon_r = int(wx_raw["daily"]["precipitation_probability_max"][2])
sunrise = sun_raw["daily"]["sunrise"][0][11:16]
sunset = sun_raw["daily"]["sunset"][0][11:16]
sr_dt = datetime.fromisoformat(sun_raw["daily"]["sunrise"][0])
ss_dt = datetime.fromisoformat(sun_raw["daily"]["sunset"][0])
wind_word = "light" if wind < 20 else "moderate"

weather = {
    "location": "Langley, BC",
    "timezone": "America/Vancouver",
    "date": "2026-11-21",
    "dateLabel": "Sat Nov 21, 2026",
    "conditions": (
        f"Saturday: high ~{hi_c}°C / low ~{lo_c}°C, rain ~{rain}%, "
        f"wind ~{wind} km/h. Sun (~{sun_r}%), Mon (~{mon_r}%)."
    ),
    "conditionsShort": "Cool, chance of rain",
    "temp": {
        "highC": hi_c,
        "lowC": lo_c,
        "highF": c_to_f(hi_c),
        "lowF": c_to_f(lo_c),
        "displayC": f"{hi_c}° / {lo_c}°C",
        "displayF": f"{c_to_f(hi_c)}° / {c_to_f(lo_c)}°F",
        "currentC": cur_c,
        "currentF": c_to_f(cur_c),
    },
    "rainChancePct": rain,
    "wind": {
        "summary": wind_word,
        "maxKmh": wind,
        "display": f"{wind_word.capitalize()}, ~{wind} km/h",
    },
    "sun": {
        "sunrise": sunrise,
        "sunset": sunset,
        "sunriseLabel": fmt_time(sr_dt).replace(" 0", " ").lstrip("0") if False else (
            f"{sr_dt.hour % 12 or 12}:{sr_dt.minute:02d} AM"
        ),
        "sunsetLabel": f"{ss_dt.hour % 12 or 12}:{ss_dt.minute:02d} PM",
        "timezoneNote": "PT",
    },
    "asOf": ASOF,
    "asOfLabel": ASOF_LABEL,
    "source": "Open-Meteo (Langley BC)",
    "lastUpdated": ASOF,
}
json.dump(weather, open("weather.json", "w"), indent=2, ensure_ascii=False)
open("weather.json", "a").write("\n")

# --- markets ---
btc_spot = round(float(json.load(open("tmp/btc_spot.json"))["data"]["amount"]))
btc_stats = json.load(open("tmp/btc_stats.json"))
gold_px = round(float(json.load(open("tmp/gold.json"))["price"]), 2)
prev_m = json.load(open("_prior_snap_20261121/markets.json"))
prev_spots = {s["id"]: s["value"] for s in prev_m["spots"]}

btc_chg_snap = pct(btc_spot, prev_spots["btc"])
gold_chg_snap = pct(gold_px, prev_spots["gold"])


def yahoo_closes(path):
    r = json.load(open(path))
    result = r["chart"]["result"][0]
    closes = result["indicators"]["quote"][0]["close"]
    ts = result["timestamp"]
    pairs = [(ts[i], closes[i]) for i in range(len(ts)) if closes[i] is not None]
    return result["meta"], pairs


_, cl_pairs = yahoo_closes("tmp/y_CLF.json")
wti = round(cl_pairs[-1][1], 2)
wti_prev = cl_pairs[-2][1]
wti_chg = pct(wti, wti_prev)
wti_delta = wti - wti_prev

_, sp_pairs = yahoo_closes("tmp/y_GSPC.json")
spx = round(sp_pairs[-1][1], 2)
spx_prev = sp_pairs[-2][1]
spx_chg = pct(spx, spx_prev)
spx_delta = spx - spx_prev

_, tnx_pairs = yahoo_closes("tmp/y_TNX.json")
tnx = round(tnx_pairs[-1][1], 3)
tnx_prev = tnx_pairs[-2][1]
tnx_pts = tnx - tnx_prev

markets = {
    "asOf": ASOF,
    "note": (
        "Sat morning PT — gold live (gold-api); WTI Friday settlement vs prior close (Yahoo); "
        "SPX/US10Y Friday close (US cash market closed); BTC Coinbase"
    ),
    "spots": [
        {
            "id": "gold",
            "name": "Spot gold",
            "symbol": "XAU",
            "value": gold_px,
            "unit": "USD/oz",
            "change": f"{gold_chg_snap:+.2f}% vs prior snap",
            "source": "gold-api.com",
            "asOf": "2026-11-21",
            "status": "live",
        },
        {
            "id": "oil",
            "name": "Spot oil (WTI)",
            "symbol": "CL",
            "value": wti,
            "unit": "USD/bbl",
            "change": f"{wti_chg:+.2f}% vs prior close",
            "source": "Yahoo CL=F",
            "asOf": "2026-11-21",
            "status": "live",
        },
        {
            "id": "btc",
            "name": "Spot BTC",
            "symbol": "BTC",
            "value": btc_spot,
            "unit": "USD",
            "change": f"{btc_chg_snap:+.2f}% vs prior snap",
            "source": "Coinbase",
            "asOf": "2026-11-21",
            "status": "live",
        },
        {
            "id": "spx",
            "name": "S&P 500",
            "symbol": "SPX",
            "value": spx,
            "unit": "index",
            "change": f"{spx_chg:+.2f}% vs prior close",
            "source": "Yahoo ^GSPC",
            "asOf": "2026-11-21",
            "status": "live",
        },
        {
            "id": "us10y",
            "name": "US 10-year Treasury",
            "symbol": "US10Y",
            "value": tnx,
            "unit": "%",
            "change": f"{tnx_pts:+.2f} pts vs prior close",
            "source": "Yahoo ^TNX",
            "asOf": "2026-11-21",
            "status": "live",
        },
    ],
}
json.dump(markets, open("markets.json", "w"), indent=2, ensure_ascii=False)
open("markets.json", "a").write("\n")


def cb(path_spot, path_stats):
    spot = float(json.load(open(path_spot))["data"]["amount"])
    stats = json.load(open(path_stats))
    openp = float(stats["open"]) if "open" in stats else None
    chg = pct(spot, openp) if openp else 0.0
    return spot, chg, stats


eth, eth_chg, _eth_s = cb("tmp/eth_spot.json", "tmp/eth_stats.json")
sol, sol_chg, _sol_s = cb("tmp/sol_spot.json", "tmp/sol_stats.json")
fet, fet_chg, _fet_s = cb("tmp/fet_spot.json", "tmp/fet_stats.json")
near, near_chg, _near_s = cb("tmp/near_spot.json", "tmp/near_stats.json")

btc_open = float(btc_stats["open"])
btc_chg_24h = pct(btc_spot, btc_open)
btc_hi = round(float(btc_stats["high"]))
btc_lo = round(float(btc_stats["low"]))

# --- data.json (preserve tasks/habits) ---
data = json.load(open("data.json"))
data["meta"]["lastUpdated"] = ASOF
data["meta"]["lastUpdatedLabel"] = ASOF_LABEL
data["weather"] = {
    "location": "Langley, BC",
    "conditionsShort": weather["conditionsShort"],
    "temp": weather["temp"],
    "rainChancePct": rain,
    "asOf": ASOF,
    "asOfLabel": ASOF_LABEL,
}

us10y_chg_display = f"{tnx_pts:+.2f} pts vs prior close"

data["primaryMarkets"] = [
    {
        "id": "xau",
        "label": "Spot gold",
        "ticker": "XAU",
        "value": gold_px,
        "display": money(round(gold_px)),
        "unit": "USD/oz",
        "change": round(gold_px - prev_spots["gold"], 2),
        "changePct": round(gold_chg_snap, 2),
        "changeDisplay": f"{gold_chg_snap:.2f}% vs prior snap",
        "asOf": ASOF,
        "source": "gold-api.com",
    },
    {
        "id": "wti",
        "label": "Spot oil (WTI)",
        "ticker": "CL",
        "value": wti,
        "display": f"${wti:.2f}",
        "unit": "USD/bbl",
        "change": round(wti_delta, 2),
        "changePct": round(wti_chg, 2),
        "changeDisplay": f"{wti_chg:.2f}% vs prior close",
        "asOf": ASOF,
        "source": "Yahoo CL=F",
    },
    {
        "id": "btc",
        "label": "Spot BTC",
        "ticker": "BTC",
        "value": btc_spot,
        "display": money(btc_spot),
        "unit": "USD",
        "change": btc_spot - prev_spots["btc"],
        "changePct": round(btc_chg_snap, 2),
        "changeDisplay": f"{btc_chg_snap:.2f}% vs prior snap",
        "asOf": ASOF,
        "source": "Coinbase",
    },
    {
        "id": "spx",
        "label": "S&P 500",
        "ticker": "SPX",
        "value": spx,
        "display": f"{spx:,.2f}",
        "unit": "index",
        "change": round(spx_delta, 2),
        "changePct": round(spx_chg, 2),
        "changeDisplay": f"{spx_chg:.2f}% vs prior close",
        "asOf": ASOF,
        "source": "Yahoo ^GSPC",
    },
    {
        "id": "us10y",
        "label": "US 10-year Treasury",
        "ticker": "US10Y",
        "value": tnx,
        "display": f"{tnx:.2f}%",
        "unit": "%",
        "change": round(tnx_pts, 3),
        "changePct": round(pct(tnx, tnx_prev), 2),
        "changeDisplay": us10y_chg_display,
        "asOf": ASOF,
        "source": "Yahoo ^TNX",
    },
]

data["watchlist"] = [
    {
        "id": "eth",
        "symbol": "ETH",
        "name": "Ethereum",
        "role": "Primary L1 settlement for agents",
        "price": round(eth, 2),
        "change24h": round(eth_chg, 2),
        "change7d": None,
        "source": "Coinbase",
        "asOf": ASOF,
    },
    {
        "id": "sol",
        "symbol": "SOL",
        "name": "Solana",
        "role": "High-throughput L1",
        "price": round(sol, 2),
        "change24h": round(sol_chg, 2),
        "change7d": None,
        "source": "Coinbase",
        "asOf": ASOF,
    },
    {
        "id": "fet",
        "symbol": "FET",
        "name": "Fetch.ai",
        "role": "Agent coin",
        "price": round(fet, 5),
        "change24h": round(fet_chg, 2),
        "change7d": None,
        "source": "Coinbase",
        "asOf": ASOF,
    },
    {
        "id": "near",
        "symbol": "NEAR",
        "name": "NEAR Protocol",
        "role": "Intents / agent protocol",
        "price": round(near, 3),
        "change24h": round(near_chg, 2),
        "change7d": None,
        "source": "Coinbase",
        "asOf": ASOF,
    },
]

data["bitcoinDetail"] = {
    "price": btc_spot,
    "change24h": round(btc_chg_24h, 2),
    "change7d": None,
    "high24h": btc_hi,
    "low24h": btc_lo,
    "marketCap": None,
    "ath": 126173,
    "athDate": "2025-10-06",
    "source": "Coinbase",
    "asOf": ASOF,
}

data["news"] = [
    {
        "title": (
            f"BTC ~{money(btc_spot)} ({btc_chg_snap:+.2f}% vs prior snap; "
            f"{btc_chg_24h:+.2f}% 24h) — 24h low ~{money(btc_lo)}"
        ),
        "source": "Coinbase",
        "date": "2026-11-21",
        "dateLabel": "Nov 21",
        "url": "https://www.coinbase.com/price/bitcoin",
    },
    {
        "title": (
            f"Agent basket: NEAR ~${near:.3f} ({near_chg:+.2f}% 24h); "
            f"FET ~${fet:.4f} ({fet_chg:+.2f}%); SOL ~${sol:.2f} ({sol_chg:+.2f}%); "
            f"ETH ~${eth:,.0f} ({eth_chg:+.2f}%)"
        ),
        "source": "Coinbase",
        "date": "2026-11-21",
        "dateLabel": "Nov 21",
        "url": "https://www.coinbase.com/price/near",
    },
    {
        "title": (
            f"Gold ~{money(round(gold_px))} ({gold_chg_snap:+.2f}%); "
            f"WTI ~${wti:.2f} ({wti_chg:+.2f}% futures vs prior close); "
            f"SPX {spx:,.2f} ({spx_chg:+.2f}%); US10Y {tnx:.2f}%"
        ),
        "source": "gold-api / Yahoo",
        "date": "2026-11-21",
        "dateLabel": "Nov 21",
        "url": "https://finance.yahoo.com/quote/%5EGSPC",
    },
    {
        "title": (
            "Today: U15 C4 Development with C1 10:45 AM LEC 3, then game at South Delta C3 4:30 PM. "
            "Clash Sunday: U17 vs North Vancouver 6:15 PM LEC 1 and U15 C4 vs Cloverdale C2 6:15 PM. "
            "New U15 practices: Thu Nov 26 6:00 PM LEC 1, Sat Dec 12 3:30 PM LEC 2. "
            "Stick & puck with Barrett this week: Tue 4:00 PM LEC, Wed 5:45 PM Aldergrove, "
            "Thu 4:00 PM LEC, Fri 4:30 PM Aldergrove."
        ),
        "source": "TeamSnap / Google Calendar",
        "date": "2026-11-21",
        "dateLabel": "Nov 21",
        "url": "https://www.teamsnap.com/",
    },
]

json.dump(data, open("data.json", "w"), indent=2, ensure_ascii=False)
open("data.json", "a").write("\n")

# --- bake index.html ---
html = open("index.html", encoding="utf-8").read()


def cls(s):
    s = re.sub(r"[·•–—]", " ", s.lower())
    s = re.sub(r"\s+", " ", s)
    if re.search(r"\bmma\s*d\b", s):
        return "cal-dayshift"
    if re.search(r"\bmma\s*a\b", s):
        return "cal-afternoon"
    if re.search(r"\bmma\s*n\b", s):
        return "cal-graveyard"
    if "u15" in s:
        return "cal-u15"
    if "u17" in s:
        return "cal-u17"
    if "u18" in s:
        return "cal-u18"
    return "cal-other"


rank = {
    "cal-dayshift": 1,
    "cal-afternoon": 2,
    "cal-graveyard": 3,
    "cal-u15": 4,
    "cal-u17": 5,
    "cal-u18": 6,
    "cal-other": 9,
}
rows = []
week_ev_lines = []
for i in range(7):
    d = TODAY + timedelta(days=i)
    ymd = d.isoformat()
    evs = [e for e in cal["events"] if e["start"][:10] == ymd]
    for e in evs:
        line = f"{ymd} {e['summary']} {e['start'][11:16]}"
        week_ev_lines.append(line)
        print(line)
    c = "dow" + (" today" if i == 0 else "") + (" has" if evs else "")
    if evs:
        if any("draft" in e["summary"].lower() for e in evs):
            best = "cal-u15"
        else:
            best = min((cls(e["summary"]) for e in evs), key=lambda k: rank[k])
        c += " " + best
    rows.append(
        f'          <div class="{c}" data-date="{ymd}"><span class="k">{d.strftime("%a")}</span><span class="d">{d.day}</span><span class="dot"></span></div>'
    )
new = (
    '<div class="weekbar" id="weekbar" aria-label="Next 7 days">\n'
    + "\n".join(rows)
    + "\n        </div>"
)
html, n1 = re.subn(
    r'<div class="weekbar" id="weekbar" aria-label="Next 7 days">.*?\n        </div>',
    lambda m: new,
    html,
    count=1,
    flags=re.S,
)
banner = (
    f'<div class="today-banner">Today · Saturday — U15 C4 Development 10:45 AM LEC 3, then game at South Delta C3 4:30 PM. '
    f"{hi_c}°/{lo_c}°C.</div>"
)
html, n2 = re.subn(
    r'<div class="today-banner">.*?</div>', lambda m: banner, html, count=1, flags=re.S
)
key = "window.__JPF_BAKED__ = "
i = html.index(key) + len(key)
_obj, end = json.JSONDecoder().raw_decode(html, i)
baked = {
    f: json.load(open(f))
    for f in ["calendar.json", "data.json", "markets.json", "weather.json", "teamsnap.json"]
}
html = html[:i] + json.dumps(baked, ensure_ascii=False) + html[end:]
open("index.html", "w", encoding="utf-8").write(html)
print(
    "weekbar",
    n1,
    "banner",
    n2,
    "baked keys",
    list(baked),
    "weekdays",
    [re.search(r'class="([^"]+)" data-date="([^"]+)"', r).groups() for r in rows],
)

# clashes next 14d (time overlap)
clashes = []
from collections import defaultdict

byday = defaultdict(list)
for e in cal["events"]:
    d = (e.get("start") or "")[:10]
    if "2026-11-21" <= d <= "2026-12-05":
        byday[d].append(e)
for d in sorted(byday):
    evs = byday[d]
    for i in range(len(evs)):
        for j in range(i + 1, len(evs)):
            a, b = evs[i], evs[j]
            a0, a1 = a.get("start"), a.get("end") or a.get("start")
            b0, b1 = b.get("start"), b.get("end") or b.get("start")
            if a0 < b1 and b0 < a1:
                clashes.append(
                    f"{date.fromisoformat(d).strftime('%a %b')} {int(d[8:])} "
                    f"{a['summary']} {a0[11:16]} / {b['summary']} {b0[11:16]}"
                )

u17_n = sum(1 for e in cal["events"] if e["id"].startswith("ts-u17-") and e["start"] >= "2026-11-21")
u15_n = sum(1 for e in cal["events"] if e["id"].startswith("ts-u15-") and e["start"] >= "2026-11-21")

stick_week = [
    f"{e['start'][:16]} {e['summary']} @ {e.get('location') or ''}"
    for e in added_stick
    if e["start"][:10] <= "2026-11-27"
]

summary = {
    "date": "2026-11-21",
    "weekbar": "2026-11-21..2026-11-27",
    "teamsnap": {
        "u17": u17_n,
        "u15c4": u15_n,
        "adds": [
            "U15 C4 Practice · LEC 1 Thu Nov 26 6:00 PM",
            "U15 C4 Practice · LEC 2 Sat Dec 12 3:30 PM",
        ],
        "moves": [],
        "cancels": [],
        "retitles": [],
        "rolledOff": [
            "U17 Dryland Fri Nov 20 8:30 PM Aim Athletic (past)",
        ],
    },
    "gcal": {
        "status": "ok_listEvents_primary",
        "note": (
            "listEvents on primary succeeded (listCalendars still missing permission). "
            "Added Stick & Puck series (Barrett) from Google. "
            "Did not import Google U15/U17 ice (TeamSnap authoritative). "
            "MMA A Dec 3–8 kept at 4:00 PM–12:00 AM PT (Google rendered 5:00 PM–1:00 AM due to America/Vancouver DST; description still says 16:00–00:00). "
            "Kevin Nelson retirement Dec 2 4–8 PM preserved (not present in this Google fetch)."
        ),
        "adds": [f"{len(added_stick)} stick-and-puck instances through 2027-03-19"] + stick_week,
        "updates": [],
        "cancels": [],
    },
    "clashes_14d": clashes,
    "markets": {
        "btc": [btc_spot, round(btc_chg_snap, 2), round(btc_chg_24h, 2), btc_lo],
        "gold": [gold_px, round(gold_chg_snap, 2)],
        "wti": [wti, round(wti_chg, 2)],
        "spx": [spx, round(spx_chg, 2)],
        "us10y": [tnx, f"{tnx_pts:+.2f} pts"],
        "near_24h": round(near_chg, 2),
        "fet_24h": round(fet_chg, 2),
        "eth_24h": round(eth_chg, 2),
        "sol_24h": round(sol_chg, 2),
    },
    "weather": {"hi": hi_c, "lo": lo_c, "rain": rain, "sunrise": weather["sun"]["sunriseLabel"]},
    "u15_ics_ok": True,
    "material": True,
    "materialReasons": [
        "TeamSnap added U15 C4 Practice Thu Nov 26 6:00 PM LEC 1 and Sat Dec 12 3:30 PM LEC 2",
        "Google Calendar recovered; added recurring Stick & Puck with Barrett (LEC Tue/Thu, Aldergrove Wed/Fri) through mid-March",
        f"Markets down: BTC ~{btc_chg_snap:.2f}% vs prior snap (24h low ~{btc_lo}), SPX ~{spx_chg:.2f}%, FET {fet_chg:.1f}% 24h, NEAR {near_chg:.1f}% 24h",
        "Standing clash Sun Nov 22: U17 vs North Vancouver 6:15 PM LEC 1 / U15 C4 vs Cloverdale C2 6:15 PM",
    ],
}
json.dump(summary, open("tmp/refresh_summary_20261121.json", "w"), indent=2, ensure_ascii=False)
open("tmp/refresh_summary_20261121.json", "a").write("\n")
print("SUMMARY", json.dumps(summary, indent=2, ensure_ascii=False))
