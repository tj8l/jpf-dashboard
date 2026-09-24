#!/usr/bin/env python3
"""Download TeamSnap ICS for LANGLEY MHA U17 A1 and merge into calendar.json.

TeamSnap is source of truth for U17 A1. Non-U17 events (MMA, U15 C, personal)
are preserved. Amanda/Google-sourced U17/U18 tryout/practice events that
overlap the TeamSnap schedule are removed and replaced.
"""
from __future__ import annotations

import json
import re
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TEAMSNAP_JSON = ROOT / "teamsnap.json"
CALENDAR_JSON = ROOT / "calendar.json"
ICS_PATH = ROOT / "teamsnap-u17a1.ics"
PT = ZoneInfo("America/Vancouver")
LA = ZoneInfo("America/Los_Angeles")
# Box tzdata for America/Vancouver is wrong after Nov 2026 DST end (stays at -07).
# TeamSnap ICS uses America/Los_Angeles; Pacific wall times match, so format via LA.
PACIFIC = LA

DEFAULT_CFG = {
    "team": "LANGLEY MHA U17 A1",
    "icsUrl": "https://ical-cdn.teamsnap.com/team_schedule/66125cfe-c4ca-41d1-82be-22e2be9960bf.ics",
    "activeOnly": True,
    "note": "Only sync this team.",
}


def load_cfg() -> dict:
    if TEAMSNAP_JSON.exists():
        return json.loads(TEAMSNAP_JSON.read_text(encoding="utf-8"))
    return dict(DEFAULT_CFG)


def download_ics(url: str, dest: Path) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "jpf-dashboard-sync/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return data


def unfold_ics(text: str) -> str:
    return re.sub(r"\r?\n[ \t]", "", text)


def parse_vevents(ics_text: str) -> list[dict]:
    text = unfold_ics(ics_text)
    events = []
    for block in re.split(r"BEGIN:VEVENT", text)[1:]:
        block = block.split("END:VEVENT", 1)[0]

        def field(name: str) -> str:
            m = re.search(rf"(?m)^{re.escape(name)}[;:](.*)$", block)
            if not m:
                return ""
            return (
                m.group(1)
                .strip()
                .replace("\\n", "\n")
                .replace("\\,", ",")
                .replace("\\;", ";")
            )

        def dt_field(name: str):
            m = re.search(rf"(?m)^{re.escape(name)}(;[^:]*)?:(.*)$", block)
            if not m:
                return None
            params, val = m.group(1) or "", m.group(2).strip()
            return parse_ics_dt(params, val)

        events.append(
            {
                "uid": field("UID"),
                "summary": field("SUMMARY"),
                "location": field("LOCATION"),
                "description": field("DESCRIPTION"),
                "start": dt_field("DTSTART"),
                "end": dt_field("DTEND"),
            }
        )
    return events


def parse_ics_dt(params: str, val: str) -> datetime | date:
    if "VALUE=DATE" in params.upper() or (len(val) == 8 and "T" not in val):
        return date(int(val[0:4]), int(val[4:6]), int(val[6:8]))
    # floating / TZID
    tz = LA
    m = re.search(r"TZID=([^;:]+)", params)
    if m:
        try:
            tz = ZoneInfo(m.group(1))
        except Exception:
            tz = LA
    if val.endswith("Z"):
        dt = datetime.strptime(val, "%Y%m%dT%H%M%SZ").replace(tzinfo=ZoneInfo("UTC"))
        return dt.astimezone(PACIFIC)
    dt = datetime.strptime(val, "%Y%m%dT%H%M%S").replace(tzinfo=tz)
    return dt.astimezone(PACIFIC)


def rink_short(desc: str, loc: str, summary: str) -> tuple[str, str]:
    """Return (title_rink_token, location_display)."""
    m = re.search(r"Location:\s*([^\n]+)", desc or "")
    rink_line = (m.group(1).strip() if m else "") or ""
    low = (rink_line + " " + loc + " " + summary).lower()

    if "aim athletic" in low:
        return "Aim Athletic", "Aim Athletic (Langley)"
    if "sportsplex" in low or "spx" in low:
        n = "2"
        rm = re.search(r"rink\s*(\d+)", low)
        if rm:
            n = rm.group(1)
        return f"SPX {n}", f"SPX {n} (Langley)"
    if "lec" in low or "langley events" in low or "arenas at lec" in low:
        n = "1"
        rm = re.search(r"rink\s*(\d+)", low)
        if rm:
            n = rm.group(1)
        return f"LEC {n}", f"LEC {n} (Langley Events Centre)"
    if "abbotsford" in low:
        return "Abbotsford", "Abbotsford Rec Centre"
    if "ridge meadows" in low or "rm " in low:
        return "Ridge Meadows", "Ridge Meadows"
    # fallback: first chunk of location or rink line
    token = rink_line.split(",")[0].strip() if rink_line else (loc.split(",")[0].strip() if loc else "")
    return token or "TBD", token or ""


def opponent_from_summary(summary: str) -> str | None:
    s = summary
    # "PreSeason at Abbotsford U17 A1" / "Preseason vs Ridge Meadows U17 A1"
    m = re.search(
        r"(?i)(?:pre-?season|game|scrimmage)\s+(?:at|vs\.?|versus)\s+(.+)$", s
    )
    if not m:
        m = re.search(r"(?i)\bat\s+([A-Za-z].+)$", s)
    if not m:
        return None
    opp = m.group(1).strip()
    opp = re.sub(r"(?i)\s*U17\s*A1\s*$", "", opp).strip()
    opp = re.sub(r"(?i)^LANGLEY MHA U17 A1\s+", "", opp).strip()
    return opp or None


def normalize_title(summary: str, rink_token: str) -> str:
    s = summary or ""
    low = s.lower()
    if "hold" in low:
        return f"U17 HOLD · {rink_token}"
    if "dryland" in low:
        return f"U17 Dryland · {rink_token}"
    if "pre-season" in low or "preseason" in low:
        opp = opponent_from_summary(s)
        if opp:
            return f"U17 PreSeason · vs {opp}"
        return f"U17 PreSeason · {rink_token}"
    if re.search(r"(?i)\b(game|scrimmage)\b", s) and "practice" not in low:
        opp = opponent_from_summary(s)
        if opp:
            return f"U17 Game · vs {opp}"
        return f"U17 Game · {rink_token}"
    # Practice / Practice/Game Day Skate
    return f"U17 Practice · {rink_token}"


def sanitize_uid(uid: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", uid).strip("-")
    return f"ts-{cleaned}"


def when_label(start: datetime | date, end: datetime | date | None) -> str:
    if isinstance(start, date) and not isinstance(start, datetime):
        day = start.strftime("%a %b %-d").replace(" 0", " ")
        return f"{day} · all day"
    assert isinstance(start, datetime)
    start = start.astimezone(PACIFIC)
    day = start.strftime("%a %b %-d").replace(" 0", " ")
    t1 = start.strftime("%-I:%M %p")
    if isinstance(end, datetime):
        end = end.astimezone(PACIFIC)
        t2 = end.strftime("%-I:%M %p")
        return f"{day} · {t1}–{t2} PT"
    return f"{day} · {t1} PT"


def iso_pt(dt: datetime | date) -> str:
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return dt.isoformat()
    # Format Pacific via LA (correct DST); label remains America/Vancouver / PT.
    return dt.astimezone(PACIFIC).isoformat(timespec="seconds")


def is_amanda_u17_u18(ev: dict) -> bool:
    """Google/Amanda-sourced U17/U18 ice events that TeamSnap replaces.

    Do NOT treat PCAHA / coach-manager meetings as Amanda hockey just because
    the title mentions U17/U18 age bands (e.g. U11–U18).
    """
    eid = str(ev.get("id") or "")
    if eid.startswith("ts-") or eid.startswith("pcaha-"):
        return False  # TeamSnap or curated PCAHA
    summary = str(ev.get("summary") or "")
    low = summary.lower()
    if "pcaha" in low or "coach/manager meeting" in low:
        return False
    if re.search(r"\bu17\b", low) or re.search(r"\bu18\b", low):
        # Admin/meeting titles that only mention age bands stay
        if "meeting" in low and not re.search(
            r"\b(practice|game|scrimmage|tryout|dryland|hold)\b", low
        ):
            return False
        return True
    if "tryout" in low and ("u17" in low or "u18" in low or "lmha" in low):
        return True
    return False


def to_teamsnap_event(raw: dict) -> dict | None:
    if not raw.get("start"):
        return None
    rink_token, loc_disp = rink_short(
        raw.get("description") or "",
        raw.get("location") or "",
        raw.get("summary") or "",
    )
    title = normalize_title(raw.get("summary") or "", rink_token)
    start = raw["start"]
    end = raw.get("end") or start
    return {
        "id": sanitize_uid(raw.get("uid") or f"{start}-{title}"),
        "summary": title,
        "location": loc_disp,
        "start": iso_pt(start),
        "end": iso_pt(end),
        "whenLabel": when_label(start, end),
    }


def event_start_date(ev: dict) -> date | None:
    s = ev.get("start") or ""
    if not s:
        return None
    try:
        if "T" in s:
            return datetime.fromisoformat(s).astimezone(PACIFIC).date()
        return date.fromisoformat(s[:10])
    except Exception:
        return None


def build_notes(events: list[dict], today: date, window_end: date) -> list[str]:
    def on_day(d: date) -> list[dict]:
        return [e for e in events if event_start_date(e) == d]

    def fmt_short(e: dict) -> str:
        s = e["summary"]
        if "T" in e.get("start", ""):
            dt = datetime.fromisoformat(e["start"]).astimezone(PACIFIC)
            t = dt.strftime("%-I:%M %p").replace(" 0", " ")
            loc = e.get("location") or ""
            short_loc = loc.split("(")[0].strip() if loc else ""
            if short_loc:
                return f"{s} {t} @ {short_loc}"
            return f"{s} {t}"
        return s

    notes = []
    todays = on_day(today)
    if todays:
        notes.append(
            f"Today {today.strftime('%a %b %-d').replace(' 0', ' ')}: "
            + "; ".join(fmt_short(e) for e in todays)
            + "."
        )
    else:
        notes.append(
            f"Today {today.strftime('%a %b %-d').replace(' 0', ' ')}: clear (no calendar events)."
        )

    fri = today + timedelta(days=1)  # often Fri when today is Thu — keep generic next clear day
    # Explicit Fri Sep 25 style note for day after today if empty
    d1 = today + timedelta(days=1)
    if not on_day(d1):
        notes.append(
            f"{d1.strftime('%a %b %-d').replace(' 0', ' ')}: clear (no calendar events)."
        )

    # Sat Sep 26 highlight when in window
    sat = date(2026, 9, 26)
    if today <= sat <= window_end:
        sat_ev = on_day(sat)
        bits = [fmt_short(e) for e in sat_ev]
        notes.append(
            "Sat Sep 26: "
            + " + ".join(bits)
            + " — book the day off (MMA D clash with U15 eval + TeamSnap U17)."
        )

    beyond = [
        e
        for e in events
        if (event_start_date(e) or date.min) > window_end
    ]
    if beyond:
        # summarize first few unique days
        days = []
        seen = set()
        for e in beyond:
            d = event_start_date(e)
            if d and d not in seen:
                seen.add(d)
                days.append(d)
            if len(days) >= 4:
                break
        day_bits = []
        for d in days:
            evs = on_day(d)
            labels = []
            for e in evs[:2]:
                labels.append(e["summary"].split(" · ")[0] if " · " in e["summary"] else e["summary"])
            day_bits.append(f"{d.strftime('%a %b %-d').replace(' 0', ' ')} ({', '.join(labels)})")
        notes.append(
            "Beyond 7-day day-list window: "
            + "; ".join(day_bits)
            + " — still in calendar.json events."
        )

    # Mention PCAHA meetings in-window (ids pcaha-*) so re-sync does not drop bulletin context
    for e in events:
        d = event_start_date(e)
        eid = str(e.get("id") or "")
        if not (d and today <= d <= window_end and eid.startswith("pcaha-")):
            continue
        when = ""
        if "T" in e.get("start", ""):
            dt = datetime.fromisoformat(e["start"]).astimezone(PACIFIC)
            when = dt.strftime("%-I:%M %p").replace(" 0", " ")
            if isinstance(e.get("end"), str) and "T" in e["end"]:
                de = datetime.fromisoformat(e["end"]).astimezone(PACIFIC)
                when = f"{when}–{de.strftime('%-I:%M %p').replace(' 0', ' ')}"
        day = d.strftime("%a %b %-d").replace(" 0", " ")
        loc = e.get("location") or "Zoom"
        notes.append(f"{day}: {e.get('summary')}{(' ' + when) if when else ''} via {loc}.")

    notes.append(
        "TeamSnap LANGLEY MHA U17 A1 is source of truth for U17; Amanda/Google U17 practices replaced. "
        "Non-U17 (MMA, U15 C) kept from Google Calendar. PCAHA meeting dates from 2026–2027 Bulletin #5."
    )
    return notes


def merge(calendar: dict, ts_events: list[dict], today: date) -> dict:
    kept = [e for e in calendar.get("events", []) if not is_amanda_u17_u18(e)]
    # Drop any prior ts- events so re-sync is idempotent
    kept = [e for e in kept if not str(e.get("id") or "").startswith("ts-")]

    cutoff = today
    incoming = []
    for raw in ts_events:
        start = raw.get("start")
        if not start:
            continue
        if isinstance(start, datetime):
            if start.astimezone(PACIFIC).date() < cutoff:
                continue
        elif isinstance(start, date) and start < cutoff:
            continue
        ev = to_teamsnap_event(raw)
        if ev:
            incoming.append(ev)

    merged = kept + incoming
    merged.sort(key=lambda e: e.get("start") or "")

    window_end = today + timedelta(days=6)
    now = datetime.now(PT).replace(microsecond=0)

    calendar["timezone"] = "America/Vancouver"
    calendar["fetchedAt"] = now.isoformat(timespec="seconds")
    calendar["source"] = (
        "Google Calendar (primary) + TeamSnap LANGLEY MHA U17 A1"
    )
    calendar["range"] = {
        "start": today.isoformat(),
        "end": window_end.isoformat(),
        "label": f"{today.strftime('%b %-d').replace(' 0', ' ')}–{window_end.strftime('%-d') if today.month == window_end.month else window_end.strftime('%b %-d').replace(' 0', ' ')} (next 7 days)",
    }
    # nicer range label like "Sep 24–30 (next 7 days)"
    if today.month == window_end.month:
        calendar["range"]["label"] = (
            f"{today.strftime('%b')} {today.day}–{window_end.day} (next 7 days)"
        )
    else:
        calendar["range"]["label"] = (
            f"{today.strftime('%b')} {today.day}–{window_end.strftime('%b')} {window_end.day} (next 7 days)"
        )
    calendar["notes"] = build_notes(merged, today, window_end)
    calendar["events"] = merged
    return calendar


def main() -> None:
    cfg = load_cfg()
    TEAMSNAP_JSON.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    url = cfg["icsUrl"]
    print(f"Downloading {url}")
    data = download_ics(url, ICS_PATH)
    text = data.decode("utf-8", errors="replace")
    raw_events = parse_vevents(text)
    print(f"Parsed {len(raw_events)} TeamSnap VEVENTs")

    calendar = json.loads(CALENDAR_JSON.read_text(encoding="utf-8"))
    today = datetime.now(PT).date()
    # Allow override via env-less default: use box "today"
    before_u17 = [e for e in calendar.get("events", []) if is_amanda_u17_u18(e)]
    print(f"Removing {len(before_u17)} Amanda/Google U17/U18 events:")
    for e in before_u17:
        print(f"  - {e.get('id')}: {e.get('summary')} @ {e.get('start')}")

    merged = merge(calendar, raw_events, today)
    CALENDAR_JSON.write_text(
        json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    ts_count = sum(1 for e in merged["events"] if str(e.get("id", "")).startswith("ts-"))
    print(
        f"Wrote calendar.json: {len(merged['events'])} events "
        f"({ts_count} TeamSnap, {len(merged['events']) - ts_count} other)"
    )


if __name__ == "__main__":
    main()
