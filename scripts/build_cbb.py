#!/usr/bin/env python3
"""Builds site/cbb-data.json (D1 men's basketball: conferences, team colors,
records and full game lists) from the open-source SportsDataverse ESPN
schedule data. Run daily by the GitHub Actions workflow."""
import csv, io, json, os, sys, urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

now = datetime.now()
SEASON = int(os.environ.get("CBB_SEASON") or (now.year + 1 if now.month >= 10 else now.year))  # season = ending year
URL = f"https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_mens_college_basketball_schedules/mbb_schedule_{SEASON}.csv"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site", "cbb-data.json")
ET = ZoneInfo("America/New_York")
CONF_NAMES = {"Am. East": "America East", "A-10": "Atlantic 10", "CUSA": "Conference USA", "MVC": "Missouri Valley",
              "Ivy": "Ivy League", "Horizon": "Horizon League", "Summit": "Summit League", "WCC": "West Coast",
              "Patriot": "Patriot League", "UAC": "United Athletic", "NEC": "Northeast", "SoCon": "Southern"}
csv.field_size_limit(sys.maxsize)
with urllib.request.urlopen(URL, timeout=180) as r:
    rows = list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))

def cid(x):
    try: return str(int(float(x)))
    except (TypeError, ValueError): return None
def num(x):
    try: return int(float(x))
    except (TypeError, ValueError): return None
def color(x):
    x = (x or "").strip().lstrip("#")
    return "#" + x if len(x) == 6 else None

confname = {}
for r in rows:
    if r["groups_is_conference"].lower() == "true" and cid(r["groups_id"]):
        confname[cid(r["groups_id"])] = CONF_NAMES.get(r["groups_short_name"], r["groups_short_name"])

teams = {}  # name -> (conf, c1, c2)
for r in rows:
    for p in ("home", "away"):
        c = cid(r[p + "_conference_id"])
        if c and c in confname:
            teams[r[p + "_location"]] = (confname[c], color(r[p + "_color"]), color(r[p + "_alternate_color"]))

games, rec, seen, last = {}, {}, set(), None
for r in sorted(rows, key=lambda r: r["date"]):
    if r["status_type_name"] not in ("STATUS_FINAL", "STATUS_SCHEDULED", "STATUS_IN_PROGRESS", "STATUS_HALFTIME", "STATUS_END_PERIOD"):
        continue
    gid = r["game_id"] or r["id"]
    if gid in seen: continue
    seen.add(gid)
    hs, as_ = num(r["home_score"]), num(r["away_score"])
    done = r["status_type_name"] == "STATUS_FINAL" and hs is not None and as_ is not None
    if not done: hs = as_ = None
    dt = datetime.strptime(r["date"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc).astimezone(ET)
    label = f"{dt:%b} {dt.day}"
    if done: last = dt
    ne = r["neutral_site"].lower() == "true"
    h, a = r["home_location"], r["away_location"]
    for t, o, s, pf, pa in ((h, a, "N" if ne else "H", hs, as_), (a, h, "N" if ne else "A", as_, hs)):
        if t not in teams: continue
        games.setdefault(t, []).append([label, o, s, pf, pa])
        if pf is not None:
            w, l = rec.get(t, (0, 0))
            rec[t] = (w + (pf > pa), l + (pf < pa))

if len(teams) < 300:
    sys.exit(f"Only {len(teams)} D1 teams found; refusing to overwrite cbb-data.json")
confs = {}
for t, (c, _, _) in teams.items():
    confs.setdefault(c, []).append(t)
confs = {c: sorted(v) for c, v in sorted(confs.items())}
out = {
    "asOf": f"{last:%b} {last.day}, {last.year}" if last else "Season not started",
    "confs": confs,
    "colors": {t: [c1 or "#667788", c2 or "#cccccc"] for t, (_, c1, c2) in teams.items()},
    "rec": {t: f"{w}-{l}" for t, (w, l) in rec.items()},
    "games": games,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print(f"{out['asOf']}: {len(teams)} teams, {len(confs)} conferences, {sum(len(v) for v in games.values())} game entries")
