#!/usr/bin/env python3
"""Daily Command Center refresh for 2026-11-24."""
import json
import re
from collections import defaultdict
from datetime import datetime, date, timedelta

ASOF = "2026-11-24T05:00:00-07:00"
ASOF_LABEL = "Tue Nov 24, 2026 · ~5:00 AM PT"
TODAY = date(2026, 11, 24)
WEEK_END = date(2026, 11, 30)
BEYOND_START = date(2026, 12, 1)
BEYOND_END = date(2026, 12, 5)


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


cal = json.load(open("calendar.json"))
cal["events"].sort(key=lambda e: (e.get("start") or "", e.get("id") or ""))


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
    label = "Today Tue Nov 24" if i == 0 else d.strftime("%a %b ") + str(d.day)
    week_notes.append(f"{label}: " + "; ".join(bits) + ".")

beyond = []
for e in cal["events"]:
    ds = (e.get("start") or "")[:10]
    if BEYOND_START.isoformat() <= ds <= BEYOND_END.isoformat():
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
    "PCAHA dates from 2026–2027 Bulletin #5. Stick & puck (Barrett) and Kevin Nelson retirement "
    "preserved from the board (Google Calendar could not be refreshed this morning). "
    "MMA A wall times kept at 4:00 PM–12:00 AM PT (spreadsheet / existing board)."
)
cal["notes"] = week_notes
cal["fetchedAt"] = ASOF
cal["range"] = {
    "start": TODAY.isoformat(),
    "end": WEEK_END.isoformat(),
    "label": "Nov 24–30 (next 7 days)",
}
json.dump(cal, open("calendar.json", "w"), indent=2, ensure_ascii=False)
open("calendar.json", "a").write("\n")
print(f"calendar events={len(cal['events'])}")

wx_raw = json.load(open("tmp/weather_om.json"))
sun_raw = json.load(open("tmp/weather_sun.json"))
hi_c = half_up(wx_raw["daily"]["temperature_2m_max"][0])
lo_c = half_up(wx_raw["daily"]["temperature_2m_min"][0])
cur_c = half_up(wx_raw["current"]["temperature_2m"])
rain = int(wx_raw["daily"]["precipitation_probability_max"][0])
wind = half_up(wx_raw["daily"]["wind_speed_10m_max"][0])
wed_r = int(wx_raw["daily"]["precipitation_probability_max"][1])
thu_r = int(wx_raw["daily"]["precipitation_probability_max"][2])
sunrise = sun_raw["daily"]["sunrise"][0][11:16]
sunset = sun_raw["daily"]["sunset"][0][11:16]
sr_dt = datetime.fromisoformat(sun_raw["daily"]["sunrise"][0])
ss_dt = datetime.fromisoformat(sun_raw["daily"]["sunset"][0])
wind_word = "light" if wind < 20 else "moderate"

weather = {
    "location": "Langley, BC",
    "timezone": "America/Vancouver",
    "date": "2026-11-24",
    "dateLabel": "Tue Nov 24, 2026",
    "conditions": (
        f"Tuesday: high ~{hi_c}°C / low ~{lo_c}°C, rain ~{rain}%, "
        f"wind ~{wind} km/h. Wed (~{wed_r}%), Thu (~{thu_r}%)."
    ),
    "conditionsShort": "Mild, rain likely",
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
        "sunriseLabel": f"{sr_dt.hour % 12 or 12}:{sr_dt.minute:02d} AM",
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

btc_spot = round(float(json.load(open("tmp/btc_spot.json"))["data"]["amount"]))
btc_stats = json.load(open("tmp/btc_stats.json"))
gold_px = round(float(json.load(open("tmp/gold.json"))["price"]), 2)
prev_m = json.load(open("_prior_snap_20261124/markets.json"))
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
        "Tue morning PT — gold live (gold-api); WTI latest session vs prior close (Yahoo); "
        "SPX/US10Y Monday close (US cash market not yet open); BTC Coinbase"
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
            "asOf": "2026-11-24",
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
            "asOf": "2026-11-24",
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
            "asOf": "2026-11-24",
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
            "asOf": "2026-11-24",
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
            "asOf": "2026-11-24",
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

# Habit week is Sun Nov 22–Sat Nov 28; do not reset mid-week.
if data.get("habitWeekStart") < "2026-11-22":
    data["habitWeekStart"] = "2026-11-22"
    data["habitWeekDays"] = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for h in data.get("habits") or []:
        h["week"] = [False, False, False, False, False, False, False]

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
        "date": "2026-11-24",
        "dateLabel": "Nov 24",
        "url": "https://www.coinbase.com/price/bitcoin",
    },
    {
        "title": (
            f"Agent basket: NEAR ~${near:.3f} ({near_chg:+.2f}% 24h); "
            f"FET ~${fet:.4f} ({fet_chg:+.2f}%); SOL ~${sol:.2f} ({sol_chg:+.2f}%); "
            f"ETH ~${eth:,.0f} ({eth_chg:+.2f}%)"
        ),
        "source": "Coinbase",
        "date": "2026-11-24",
        "dateLabel": "Nov 24",
        "url": "https://www.coinbase.com/price/near",
    },
    {
        "title": (
            f"Gold ~{money(round(gold_px))} ({gold_chg_snap:+.2f}%); "
            f"WTI ~${wti:.2f} ({wti_chg:+.2f}% futures vs prior close); "
            f"SPX {spx:,.2f} ({spx_chg:+.2f}%); US10Y {tnx:.2f}%"
        ),
        "source": "gold-api / Yahoo",
        "date": "2026-11-24",
        "dateLabel": "Nov 24",
        "url": "https://finance.yahoo.com/quote/%5EGSPC",
    },
    {
        "title": (
            "Today: U15 C4 Practice 6:00 AM SPX 2; Stick & puck with Barrett 4:00 PM LEC Arena 3. "
            "This week: Wed U17 Development 7:00 PM LEC 2; "
            "Thu U15 practice 6:00 PM LEC 1 and U17 vs Richmond 9:15 PM at Richmond Ice Centre; "
            "Sat U15 Development with C2 10:45 AM LEC 3. "
            "Sunday clash: U17 vs North Delta 6:15 PM LEC 1 and U15 vs Semiahmoo C1 7:00 PM LEC 2. "
            "Stick & puck also Wed 5:45 PM Aldergrove, Thu 4:00 PM LEC, Fri 4:30 PM Aldergrove."
        ),
        "source": "TeamSnap / Google Calendar",
        "date": "2026-11-24",
        "dateLabel": "Nov 24",
        "url": "https://www.teamsnap.com/",
    },
]

json.dump(data, open("data.json", "w"), indent=2, ensure_ascii=False)
open("data.json", "a").write("\n")

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
for i in range(7):
    d = TODAY + timedelta(days=i)
    ymd = d.isoformat()
    evs = [e for e in cal["events"] if e["start"][:10] == ymd]
    for e in evs:
        print(f"{ymd} {e['summary']} {e['start'][11:16]}")
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
    f'<div class="today-banner">Today · Tuesday — U15 C4 Practice 6:00 AM SPX 2. '
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

clashes = []
byday = defaultdict(list)
for e in cal["events"]:
    d = (e.get("start") or "")[:10]
    if "2026-11-24" <= d <= "2026-12-08":
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

u17_n = sum(1 for e in cal["events"] if e["id"].startswith("ts-u17-") and e["start"] >= "2026-11-24")
u15_n = sum(1 for e in cal["events"] if e["id"].startswith("ts-u15-") and e["start"] >= "2026-11-24")

material_reasons = []
if abs(btc_chg_snap) >= 3 or abs(near_chg) >= 5 or abs(gold_chg_snap) >= 2:
    material_reasons.append(
        f"Markets: BTC ~{btc_chg_snap:.2f}% vs prior snap (24h {btc_chg_24h:+.2f}%), "
        f"NEAR {near_chg:+.1f}% 24h, gold {gold_chg_snap:+.2f}%"
    )
if abs(wti_chg) >= 2:
    material_reasons.append(f"WTI {wti_chg:+.2f}% vs prior close (~${wti:.2f})")
if abs(spx_chg) >= 2:
    material_reasons.append(f"SPX {spx_chg:+.2f}% vs prior close ({spx:,.2f})")

# Upcoming (not new): Sun Nov 29 U17 vs North Delta 6:15 PM LEC 1 overlaps U15 vs Semiahmoo C1 7:00 PM LEC 2.

summary = {
    "date": "2026-11-24",
    "weekbar": "2026-11-24..2026-11-30",
    "teamsnap": {
        "u17": u17_n,
        "u15c4": u15_n,
        "adds": [],
        "moves": [],
        "cancels": [],
        "retitles": [],
        "rolledOff": [
            "U17 Practice Mon Nov 23 9:30 PM SPX 2 (past)",
        ],
    },
    "gcal": {
        "status": "auth_failed_need_permission",
        "note": (
            "listCalendars and listEvents on primary failed this morning "
            "(Google Calendar needs a missing permission / reconnect). "
            "Did not mutate personal events. Preserved stick & puck, Kevin Nelson retirement, and MMA A. "
            "A Google Calendar connect card is already in chat. "
            "Did not pause the daily refresh; TeamSnap / markets / weather still updated."
        ),
        "adds": [],
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
    "weather": {"hi": hi_c, "lo": lo_c, "rain": rain, "wind": wind, "sunrise": weather["sun"]["sunriseLabel"]},
    "u15_ics_ok": True,
    "habitWeekStart": data.get("habitWeekStart"),
    "material": bool(material_reasons),
    "materialReasons": material_reasons,
}
json.dump(summary, open("tmp/refresh_summary_20261124.json", "w"), indent=2, ensure_ascii=False)
open("tmp/refresh_summary_20261124.json", "a").write("\n")
print("SUMMARY", json.dumps(summary, indent=2, ensure_ascii=False))
