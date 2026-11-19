#!/usr/bin/env python3
"""Daily Command Center refresh for 2026-11-19."""
import json
import re
from datetime import date, timedelta

ASOF = "2026-11-19T05:00:00-07:00"
ASOF_LABEL = "Thu Nov 19, 2026 · ~5:00 AM PT"
TODAY = date(2026, 11, 19)


def half_up(x):
    return int(x + 0.5) if x >= 0 else int(x - 0.5)


def c_to_f(c):
    return half_up(c * 9 / 5 + 32)


def pct(new, old):
    return (new - old) / old * 100


def money(n, decimals=0):
    if decimals == 0:
        return f"\${n:,.0f}"
    return f"\${n:,.{decimals}f}"


# --- weather ---
wx_raw = json.load(open("tmp/weather_om.json"))
hi_c = half_up(wx_raw["daily"]["temperature_2m_max"][0])
lo_c = half_up(wx_raw["daily"]["temperature_2m_min"][0])
cur_c = half_up(wx_raw["current"]["temperature_2m"])
rain = int(wx_raw["daily"]["precipitation_probability_max"][0])
wind = half_up(wx_raw["daily"]["wind_speed_10m_max"][0])
fri_r = int(wx_raw["daily"]["precipitation_probability_max"][1])
sat_r = int(wx_raw["daily"]["precipitation_probability_max"][2])

weather = {
    "location": "Langley, BC",
    "timezone": "America/Vancouver",
    "date": "2026-11-19",
    "dateLabel": "Thu Nov 19, 2026",
    "conditions": (
        f"Thursday: high ~{hi_c}\u00b0C / low ~{lo_c}\u00b0C, rain ~{rain}%, "
        f"wind ~{wind} km/h. Fri (~{fri_r}%), Sat (~{sat_r}%)."
    ),
    "conditionsShort": "Cool",
    "temp": {
        "highC": hi_c,
        "lowC": lo_c,
        "highF": c_to_f(hi_c),
        "lowF": c_to_f(lo_c),
        "displayC": f"{hi_c}\u00b0 / {lo_c}\u00b0C",
        "displayF": f"{c_to_f(hi_c)}\u00b0 / {c_to_f(lo_c)}\u00b0F",
        "currentC": cur_c,
        "currentF": c_to_f(cur_c),
    },
    "rainChancePct": rain,
    "wind": {
        "summary": "light",
        "maxKmh": wind,
        "display": f"Light, ~{wind} km/h",
    },
    "sun": {
        "sunrise": "08:26",
        "sunset": "17:24",
        "sunriseLabel": "8:26 AM",
        "sunsetLabel": "5:24 PM",
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
prev_m = json.load(open("_prior_snap_20261119/markets.json"))
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
        "Thu pre-open PT \u2014 gold live (gold-api); WTI futures vs prior close (Yahoo); "
        "SPX/US10Y latest close (US cash market not open yet); BTC Coinbase"
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
            "asOf": "2026-11-19",
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
            "asOf": "2026-11-19",
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
            "asOf": "2026-11-19",
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
            "asOf": "2026-11-19",
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
            "asOf": "2026-11-19",
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

# --- data.json ---
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

# us10y changeDisplay: keep signed format like "-0.02 pts vs prior close"
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
        "display": f"\${wti:.2f}",
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
        "role": "High-throughput agent txs",
        "price": round(sol, 2),
        "change24h": round(sol_chg, 2),
        "change7d": None,
        "source": "Coinbase",
        "asOf": ASOF,
    },
    {
        "id": "usdc",
        "symbol": "USDC",
        "name": "USD Coin",
        "role": "Stable unit for on-chain payments",
        "price": 1.0,
        "change24h": 0.0,
        "change7d": 0.0,
        "source": "Coinbase",
        "asOf": ASOF,
    },
    {
        "id": "fet",
        "symbol": "FET",
        "name": "ASI Alliance (Fetch.ai)",
        "role": "Agent-economy token",
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
            f"{btc_chg_24h:+.2f}% 24h) \u2014 24h low ~{money(btc_lo)}"
        ),
        "source": "Coinbase",
        "date": "2026-11-19",
        "dateLabel": "Nov 19",
        "url": "https://www.coinbase.com/price/bitcoin",
    },
    {
        "title": (
            f"Agent basket: NEAR ~\${near:.3f} ({near_chg:+.2f}% 24h); "
            f"FET ~\${fet:.4f} ({fet_chg:+.2f}%); SOL ~\${sol:.2f} ({sol_chg:+.2f}%); "
            f"ETH ~\${eth:,.0f} ({eth_chg:+.2f}%)"
        ),
        "source": "Coinbase",
        "date": "2026-11-19",
        "dateLabel": "Nov 19",
        "url": "https://www.coinbase.com/price/near",
    },
    {
        "title": (
            f"Gold ~{money(round(gold_px))} ({gold_chg_snap:+.2f}%); "
            f"WTI ~\${wti:.2f} ({wti_chg:+.2f}% futures vs prior close); "
            f"SPX {spx:,.2f} ({spx_chg:+.2f}%); US10Y {tnx:.2f}%"
        ),
        "source": "gold-api / Yahoo",
        "date": "2026-11-19",
        "dateLabel": "Nov 19",
        "url": "https://finance.yahoo.com/quote/%5EGSPC",
    },
    {
        "title": (
            "Today: U15 C4 Practice 6:15 PM SPX 1; U17 Practice 9:15 PM SPX 2. "
            "Clash Sunday: U17 vs North Vancouver 6:15 PM LEC 1 and U15 C4 at Cloverdale 6:15 PM. "
            "TeamSnap moved U15 practice from Tue Dec 8 6 AM SPX 2 to Wed Dec 9 5 PM LEC 3."
        ),
        "source": "TeamSnap / LMHA",
        "date": "2026-11-19",
        "dateLabel": "Nov 19",
        "url": "https://www.teamsnap.com/",
    },
]

json.dump(data, open("data.json", "w"), indent=2, ensure_ascii=False)
open("data.json", "a").write("\n")

# --- bake index.html ---
html = open("index.html", encoding="utf-8").read()
cal = json.load(open("calendar.json"))


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
        print(ymd, e["summary"], e["start"][11:16])
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
    f'<div class="today-banner">Today · Thursday — U15 C4 Practice 6:15 PM SPX 1; '
    f"U17 Practice 9:15 PM SPX 2. {hi_c}\u00b0/{lo_c}\u00b0C.</div>"
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

summary = {
    "date": "2026-11-19",
    "weekbar": "2026-11-19..2026-11-25",
    "teamsnap": {
        "u17": 28,
        "u15c4": 25,
        "adds": [],
        "moves": [
            "U15 C4 Practice from Tue Dec 8 6:00-7:00 AM SPX 2 to Wed Dec 9 5:00-6:00 PM LEC 3"
        ],
        "cancels": [],
        "retitles": [],
        "rolledOff": ["U17 Development Wed Nov 18 7:00 PM LEC 2 (past)"],
    },
    "gcal": {
        "status": "auth_failed",
        "note": "Google Calendar connector needs re-auth (missing permission). Existing MMA/personal/PCAHA events preserved; no GCal add/move/cancel check today.",
        "adds": [],
        "updates": [],
        "cancels": [],
    },
    "clashes_7d": [
        "Sun Nov 22 U17 vs North Vancouver 6:15 PM LEC 1 / U15 C4 at Cloverdale 6:15 PM (standing)"
    ],
    "markets": {
        "btc": [btc_spot, round(btc_chg_snap, 2)],
        "gold": [gold_px, round(gold_chg_snap, 2)],
        "wti": [wti, round(wti_chg, 2)],
        "spx": [spx, round(spx_chg, 2)],
        "us10y": [tnx, f"{tnx_pts:+.2f} pts"],
    },
    "weather": {"hi": hi_c, "lo": lo_c, "rain": rain, "sunrise": "8:26 AM"},
    "u15_ics_ok": True,
    "material": True,
    "materialReasons": [
        "TeamSnap moved U15 C4 Practice from Tue Dec 8 6 AM SPX 2 to Wed Dec 9 5 PM LEC 3"
    ],
}
json.dump(summary, open("tmp/refresh_summary_20261119.json", "w"), indent=2, ensure_ascii=False)
open("tmp/refresh_summary_20261119.json", "a").write("\n")
print("SUMMARY", json.dumps(summary, indent=2))
