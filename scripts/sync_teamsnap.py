#!/usr/bin/env python3
"""Download TeamSnap ICS for LANGLEY MHA U17 A1 + U15 C4 and merge into calendar.json.

TeamSnap is source of truth for both U17 A1 and U15 C4 ice. Amanda/Google-sourced
U17/U18 and Google-sourced U15 C / U15 C4 ice are removed and replaced. MMA,
personal, PCAHA meetings, and non-hockey items are preserved.

Backward compatible: a legacy teamsnap.json with a single top-level icsUrl is
treated as U17-only.
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
PT = ZoneInfo("America/Vancouver")
LA = ZoneInfo("America/Los_Angeles")
# Box tzdata for America/Vancouver is wrong after Nov 2026 DST end (stays at -07).
# TeamSnap ICS uses America/Los_Angeles; Pacific wall times match, so format via LA.
PACIFIC = LA

DEFAULT_U17 = {
    "id": "u17a1",
    "team": "LANGLEY MHA U17 A1",
    "labelPrefix": "U17",
    "colorHint": "yellow",
    "icsUrl": "https://ical-cdn.teamsnap.com/team_schedule/66125cfe-c4ca-41d1-82be-22e2be9960bf.ics",
    "icsFile": "teamsnap-u17a1.ics",
    "idPrefix": "ts-u17-",
}

DEFAULT_CFG = {
    "teams": [DEFAULT_U17],
    "activeOnly": True,
    "syncThrough": "2027-03-20",
    "note": "Sync U17 A1 from TeamSnap.",
}


def load_cfg() -> dict:
    if not TEAMSNAP_JSON.exists():
        return dict(DEFAULT_CFG)
    raw = json.loads(TEAMSNAP_JSON.read_text(encoding="utf-8"))
    # Legacy single-team shape: top-level icsUrl → treat as U17 only.
    if "teams" not in raw and raw.get("icsUrl"):
        team = dict(DEFAULT_U17)
        team["icsUrl"] = raw["icsUrl"]
        if raw.get("team"):
            team["team"] = raw["team"]
        return {
            "teams": [team],
            "activeOnly": bool(raw.get("activeOnly", True)),
            "syncThrough": raw.get("syncThrough") or DEFAULT_CFG["syncThrough"],
            "note": raw.get("note") or "Legacy single-team sync (U17).",
        }
    if "teams" not in raw:
        return dict(DEFAULT_CFG)
    return raw


def normalize_teams(cfg: dict) -> list[dict]:
    teams = []
    for t in cfg.get("teams") or []:
        team = dict(t)
        tid = (team.get("id") or "").lower()
        if not team.get("idPrefix"):
            if "u15" in tid:
                team["idPrefix"] = "ts-u15-"
            else:
                team["idPrefix"] = "ts-u17-"
        if not team.get("labelPrefix"):
            if "u15" in tid:
                team["labelPrefix"] = "U15 C4"
            else:
                team["labelPrefix"] = "U17"
        if not team.get("icsFile"):
            team["icsFile"] = f"teamsnap-{team.get('id') or 'team'}.ics"
        teams.append(team)
    return teams


def download_ics(url: str, dest: Path) -> bytes:
    # Prefer https; follow redirects.
    if url.startswith("http://"):
        url = "https://" + url[len("http://") :]
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
        rm = re.search(r"(?:spx|rink)\s*(\d+)", low)
        if rm:
            n = rm.group(1)
        return f"SPX {n}", f"SPX {n} (Langley)"
    if "lec" in low or "langley events" in low or "arenas at lec" in low:
        if "meeting room" in low or "video room" in low:
            rm = re.search(r"meeting room\s*([a-z0-9]+)", low) or re.search(
                r"video room\s*([a-z0-9]+)", low
            )
            room = rm.group(1).upper() if rm else "F"
            return f"LEC Room {room}", f"LEC Meeting Room {room} (Langley Events Centre)"
        n = "1"
        rm = re.search(r"rink\s*(\d+)", low)
        if rm:
            n = rm.group(1)
        return f"LEC {n}", f"LEC {n} (Langley Events Centre)"
    if "cloverdale" in low:
        color = ""
        cm = re.search(r"\((blue|red|green|orange)\)", low)
        if cm:
            color = f" ({cm.group(1).title()})"
        rm = re.search(r"rink\s*(\d+)", low)
        n = rm.group(1) if rm else ""
        token = f"Cloverdale {n}".strip() if n else "Cloverdale"
        return token, f"Cloverdale Sport & Ice Complex{color}"
    if "newton" in low:
        return "Newton", "Newton Arena (Surrey)"
    if "sungod" in low:
        return "Sungod", "Sungod Recreation Centre"
    if "semiahmoo" in low or re.search(r"\bsemi\b", low):
        return "Semiahmoo", "Semiahmoo (South Surrey)"
    if "abbotsford" in low:
        return "Abbotsford", "Abbotsford Rec Centre"
    if "ridge meadows" in low or re.search(r"\brm\b", low):
        return "Ridge Meadows", "Ridge Meadows"
    if "south delta" in low:
        return "South Delta", "South Delta"
    if "north delta" in low:
        return "North Delta", "North Delta"
    token = (
        rink_line.split(",")[0].strip()
        if rink_line
        else (loc.split(",")[0].strip() if loc else "")
    )
    return token or "TBD", token or ""


def _strip_team_suffixes(opp: str, team_name: str, label_prefix: str) -> str:
    opp = opp.strip()
    # Drop leading own-team / game-code crumbs
    opp = re.sub(re.escape(team_name), "", opp, flags=re.I).strip()
    opp = re.sub(r"(?i)\bU15[EQ]\d+\b", "", opp).strip()
    opp = re.sub(r"(?i)\bU17[EQ]\d+\b", "", opp).strip()
    # Intra-Langley U15: LANGLEY MHA U15 C2 → C2 (before generic MHA strip)
    m = re.search(r"(?i)LANGLEY\s+MHA\s+U15\s+C(\d+)\s*$", opp)
    if m:
        return f"C{m.group(1)}"
    # Normalize compact MHA forms: Cloverdale MHAU15C3 → Cloverdale C3
    opp = re.sub(r"(?i)\bMHA\s*U15\s*C(\d+)\b", r"C\1", opp)
    opp = re.sub(r"(?i)\bMHAU15C(\d+)\b", r"C\1", opp)
    opp = re.sub(r"(?i)\bMHA\s*U17\s*A1\b", "", opp).strip()
    opp = re.sub(r"(?i)\bU17\s*A1\s*$", "", opp).strip()
    # Semi → Semiahmoo when alone / leading
    opp = re.sub(r"(?i)^Semi\b", "Semiahmoo", opp).strip()
    # South Delta / Cloverdale already cleaned to "… C1" style
    opp = re.sub(r"\s+", " ", opp).strip(" -–—")
    # Drop own label prefix if present
    opp = re.sub(rf"(?i)^{re.escape(label_prefix)}\s+", "", opp).strip()
    return opp or None


def opponent_from_summary(summary: str, team_name: str, label_prefix: str) -> str | None:
    s = summary or ""
    # Strip own team name prefix for parsing
    s_work = re.sub(re.escape(team_name), "", s, flags=re.I).strip(" -–—")
    s_work = re.sub(r"(?i)\bU15[EQ]\d+\b", "", s_work).strip(" -–—")

    m = re.search(
        r"(?i)(?:pre-?season|league|game|scrimmage|interleague)\s+(?:at|vs\.?|versus)\s+(.+)$",
        s_work,
    )
    if not m:
        m = re.search(r"(?i)\b(?:at|vs\.?|versus)\s+(.+)$", s)
    if not m:
        # Development - U15C4 & C1
        m = re.search(r"(?i)development\s*[-–—:]?\s*(?:U15C\d+\s*[&+]\s*)?(.+)$", s_work)
        if m:
            opp = m.group(1).strip()
            opp = re.sub(r"(?i)^U15C\d+\s*[&+]\s*", "", opp).strip()
            opp = _strip_team_suffixes(opp, team_name, label_prefix)
            return opp
        return None
    opp = _strip_team_suffixes(m.group(1), team_name, label_prefix)
    return opp


def normalize_title(summary: str, rink_token: str, team: dict) -> str:
    s = summary or ""
    low = s.lower()
    prefix = team.get("labelPrefix") or "U17"
    team_name = team.get("team") or ""

    if "parent" in low and "meeting" in low:
        return f"{prefix} Parent's Meeting · {rink_token}"
    if "hold" in low:
        return f"{prefix} HOLD · {rink_token}"
    if "dryland" in low:
        return f"{prefix} Dryland · {rink_token}"
    if "development" in low:
        opp = opponent_from_summary(s, team_name, prefix)
        if opp:
            return f"{prefix} Development · with {opp}"
        return f"{prefix} Development · {rink_token}"
    if "interleague" in low:
        opp = opponent_from_summary(s, team_name, prefix)
        if opp:
            return f"{prefix} Interleague · vs {opp}"
        return f"{prefix} Interleague · {rink_token}"
    if "pre-season" in low or "preseason" in low:
        opp = opponent_from_summary(s, team_name, prefix)
        if opp:
            return f"{prefix} PreSeason · vs {opp}"
        return f"{prefix} PreSeason · {rink_token}"
    if re.search(r"(?i)\bleague\b", s) and "practice" not in low:
        opp = opponent_from_summary(s, team_name, prefix)
        if opp:
            return f"{prefix} League · vs {opp}"
        return f"{prefix} League · {rink_token}"
    # Game codes / at / vs without explicit "game" word (common on U15 ICS)
    if (
        re.search(r"(?i)\b(game|scrimmage)\b", s)
        or re.search(r"(?i)\bU15[EQ]\d+\b", s)
        or re.search(r"(?i)\b(?:at|vs\.?|versus)\b", s)
    ) and "practice" not in low and "development" not in low:
        opp = opponent_from_summary(s, team_name, prefix)
        # Prefer "at X" wording when summary uses at (away)
        at_away = bool(re.search(r"(?i)\bat\b", s)) and not bool(
            re.search(r"(?i)\bvs\.?\b", s)
        )
        if opp:
            if at_away and "u15" in (team.get("id") or "").lower():
                return f"{prefix} Game · at {opp}"
            return f"{prefix} Game · vs {opp}"
        return f"{prefix} Game · {rink_token}"
    # Practice / Practice/Game Day Skate
    return f"{prefix} Practice · {rink_token}"


def sanitize_uid(uid: str, id_prefix: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", uid).strip("-")
    # Avoid double-prefix if uid already cleaned oddly
    return f"{id_prefix}{cleaned}"


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
        if end != start:
            t2 = end.strftime("%-I:%M %p")
            return f"{day} · {t1}–{t2} PT"
    return f"{day} · {t1} PT"


def iso_pt(dt: datetime | date) -> str:
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return dt.isoformat()
    return dt.astimezone(PACIFIC).isoformat(timespec="seconds")


def is_amanda_u17_u18(ev: dict) -> bool:
    """Google/Amanda-sourced U17/U18 ice events that TeamSnap replaces."""
    eid = str(ev.get("id") or "")
    if eid.startswith("ts-") or eid.startswith("pcaha-"):
        return False
    summary = str(ev.get("summary") or "")
    low = summary.lower()
    if "pcaha" in low or "coach/manager meeting" in low:
        return False
    if re.search(r"\bu17\b", low) or re.search(r"\bu18\b", low):
        if "meeting" in low and not re.search(
            r"\b(practice|game|scrimmage|tryout|dryland|hold)\b", low
        ):
            return False
        return True
    if "tryout" in low and ("u17" in low or "u18" in low or "lmha" in low):
        return True
    return False


def is_google_u15_ice(ev: dict) -> bool:
    """Google-sourced U15 C / U15 C4 ice that TeamSnap replaces.

    Keeps Draft, jersey pickup, PCAHA, MMA, and unrelated personal events.
    """
    eid = str(ev.get("id") or "")
    if eid.startswith("ts-") or eid.startswith("pcaha-"):
        return False
    summary = str(ev.get("summary") or "")
    low = summary.lower()
    if "pcaha" in low or "coach/manager meeting" in low:
        return False
    if re.search(r"\bmma\b", low):
        return False
    # Must look like U15 C / U15 C4 / LMHA U15
    if not (
        re.search(r"\bu15\s*c\d*\b", low)
        or re.search(r"\blmha\s*u15\b", low)
        or re.search(r"\bu15c\d*\b", low)
    ):
        return False
    # Non-ice admin stays
    if re.search(r"\b(draft|jersey|gear\s*pickup|parent.?s?\s*meeting|meeting)\b", low):
        if not re.search(
            r"\b(practice|game|scrimmage|interleague|development|eval|hold|dryland)\b",
            low,
        ):
            return False
    # Ice activities TeamSnap owns
    if re.search(
        r"\b(practice|game|scrimmage|interleague|development|eval|hold|dryland)\b",
        low,
    ):
        return True
    # "U15 C4 … vs/at …" game-style titles without the word game
    if re.search(r"\b(vs\.?|at|versus)\b", low):
        return True
    return False


def to_teamsnap_event(raw: dict, team: dict) -> dict | None:
    if not raw.get("start"):
        return None
    rink_token, loc_disp = rink_short(
        raw.get("description") or "",
        raw.get("location") or "",
        raw.get("summary") or "",
    )
    title = normalize_title(raw.get("summary") or "", rink_token, team)
    start = raw["start"]
    end = raw.get("end") or start
    return {
        "id": sanitize_uid(
            raw.get("uid") or f"{start}-{title}", team.get("idPrefix") or "ts-"
        ),
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


def raw_start_date(start) -> date | None:
    if isinstance(start, datetime):
        return start.astimezone(PACIFIC).date()
    if isinstance(start, date):
        return start
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

    d1 = today + timedelta(days=1)
    if not on_day(d1):
        notes.append(
            f"{d1.strftime('%a %b %-d').replace(' 0', ' ')}: clear (no calendar events)."
        )

    beyond = [
        e for e in events if (event_start_date(e) or date.min) > window_end
    ]
    if beyond:
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
                labels.append(
                    e["summary"].split(" · ")[0]
                    if " · " in e["summary"]
                    else e["summary"]
                )
            day_bits.append(
                f"{d.strftime('%a %b %-d').replace(' 0', ' ')} ({', '.join(labels)})"
            )
        notes.append(
            "Beyond 7-day day-list window: "
            + "; ".join(day_bits)
            + " — still in calendar.json events."
        )

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
        notes.append(
            f"{day}: {e.get('summary')}{(' ' + when) if when else ''} via {loc}."
        )

    notes.append(
        "TeamSnap LANGLEY MHA U17 A1 + U15 C4 is source of truth for both teams' ice; "
        "Amanda/Google U17 and Google U15 C/C4 ice replaced. "
        "MMA, personal, and PCAHA meetings preserved. PCAHA dates from 2026–2027 Bulletin #5."
    )
    return notes


def merge(
    calendar: dict,
    incoming_events: list[dict],
    today: date,
    sync_through: date,
    team_labels: list[str],
) -> dict:
    def drop_u15(e: dict) -> bool:
        # Only drop Google U15 ice from today forward (TeamSnap window).
        # Keep historical evals / past ice for day-list context.
        if not is_google_u15_ice(e):
            return False
        d = event_start_date(e)
        return d is None or d >= today

    removed_u17 = [e for e in calendar.get("events", []) if is_amanda_u17_u18(e)]
    removed_u15 = [e for e in calendar.get("events", []) if drop_u15(e)]
    kept = [
        e
        for e in calendar.get("events", [])
        if not is_amanda_u17_u18(e) and not drop_u15(e)
    ]
    # Drop any prior ts- events so re-sync is idempotent (old ts- and new ts-u17-/ts-u15-)
    kept = [e for e in kept if not str(e.get("id") or "").startswith("ts-")]

    merged = kept + incoming_events
    merged.sort(key=lambda e: e.get("start") or "")

    window_end = today + timedelta(days=6)
    now = datetime.now(PT).replace(microsecond=0)

    labels = " + ".join(team_labels) if team_labels else "TeamSnap"
    calendar["timezone"] = "America/Vancouver"
    calendar["fetchedAt"] = now.isoformat(timespec="seconds")
    calendar["source"] = f"Google Calendar (primary) + TeamSnap {labels}"
    if today.month == window_end.month:
        range_label = f"{today.strftime('%b')} {today.day}–{window_end.day} (next 7 days)"
    else:
        range_label = (
            f"{today.strftime('%b')} {today.day}–{window_end.strftime('%b')} {window_end.day} (next 7 days)"
        )
    calendar["range"] = {
        "start": today.isoformat(),
        "end": window_end.isoformat(),
        "label": range_label,
    }
    calendar["notes"] = build_notes(merged, today, window_end)
    calendar["events"] = merged
    calendar["_syncMeta"] = {
        "syncThrough": sync_through.isoformat(),
        "removedAmandaU17": len(removed_u17),
        "removedGoogleU15Ice": len(removed_u15),
        "removedGoogleU15Titles": [
            f"{e.get('start', '')[:10]} {e.get('summary')}" for e in removed_u15
        ],
    }
    return calendar


def filter_window(raw_events: list[dict], today: date, sync_through: date) -> list[dict]:
    out = []
    for raw in raw_events:
        d = raw_start_date(raw.get("start"))
        if d is None:
            continue
        if d < today:
            continue
        if d > sync_through:
            continue
        out.append(raw)
    return out


def main() -> None:
    cfg = load_cfg()
    teams = normalize_teams(cfg)
    # Persist normalized multi-team config (keeps shape stable for Pages bake)
    out_cfg = {
        "teams": teams,
        "activeOnly": bool(cfg.get("activeOnly", True)),
        "syncThrough": cfg.get("syncThrough") or DEFAULT_CFG["syncThrough"],
        "note": cfg.get("note")
        or "Sync U17 A1 + U15 C4 from TeamSnap through 2027-03-20. TeamSnap is source of truth for both.",
    }
    TEAMSNAP_JSON.write_text(json.dumps(out_cfg, indent=2) + "\n", encoding="utf-8")

    sync_through = date.fromisoformat(out_cfg["syncThrough"])
    today = datetime.now(PT).date()

    all_incoming: list[dict] = []
    team_labels: list[str] = []
    counts: dict[str, int] = {}

    for team in teams:
        url = team["icsUrl"]
        dest = ROOT / team["icsFile"]
        print(f"Downloading [{team.get('id')}] {url}")
        data = download_ics(url, dest)
        text = data.decode("utf-8", errors="replace")
        raw_events = parse_vevents(text)
        print(f"  Parsed {len(raw_events)} VEVENTs")
        windowed = filter_window(raw_events, today, sync_through)
        converted = []
        for raw in windowed:
            ev = to_teamsnap_event(raw, team)
            if ev:
                converted.append(ev)
        print(
            f"  Keeping {len(converted)} events from {today.isoformat()} through {sync_through.isoformat()}"
        )
        all_incoming.extend(converted)
        label = team.get("team") or team.get("id")
        team_labels.append(label)
        counts[team.get("id") or label] = len(converted)

    calendar = json.loads(CALENDAR_JSON.read_text(encoding="utf-8"))
    before_u17 = [e for e in calendar.get("events", []) if is_amanda_u17_u18(e)]
    before_u15 = [
        e
        for e in calendar.get("events", [])
        if is_google_u15_ice(e)
        and ((event_start_date(e) or date.min) >= today)
    ]
    print(f"Removing {len(before_u17)} Amanda/Google U17/U18 events:")
    for e in before_u17:
        print(f"  - {e.get('id')}: {e.get('summary')} @ {e.get('start')}")
    print(f"Removing {len(before_u15)} Google U15 C/C4 ice events:")
    for e in before_u15:
        print(f"  - {e.get('id')}: {e.get('summary')} @ {e.get('start')}")

    merged = merge(calendar, all_incoming, today, sync_through, team_labels)
    meta = merged.pop("_syncMeta", {})
    CALENDAR_JSON.write_text(
        json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    u17_n = sum(1 for e in merged["events"] if str(e.get("id", "")).startswith("ts-u17-"))
    u15_n = sum(1 for e in merged["events"] if str(e.get("id", "")).startswith("ts-u15-"))
    legacy_ts = sum(
        1
        for e in merged["events"]
        if str(e.get("id", "")).startswith("ts-")
        and not str(e.get("id", "")).startswith("ts-u17-")
        and not str(e.get("id", "")).startswith("ts-u15-")
    )
    print(
        f"Wrote calendar.json: {len(merged['events'])} events "
        f"(ts-u17={u17_n}, ts-u15={u15_n}, legacy-ts={legacy_ts}, "
        f"other={len(merged['events']) - u17_n - u15_n - legacy_ts})"
    )
    print(f"Per-team incoming counts: {counts}")
    print(f"syncThrough={meta.get('syncThrough')} removedGoogleU15Ice={meta.get('removedGoogleU15Ice')}")


if __name__ == "__main__":
    main()
