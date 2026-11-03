#!/usr/bin/env python3
"""Builds site/records.json (team records + game lists) from the open-source
cfbfastR schedule data on GitHub. Run daily by the GitHub Actions workflow."""
import csv, io, json, os, sys, urllib.request
from datetime import datetime, timedelta, timezone

SEASON = int(os.environ.get("SEASON") or (datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1))
URL = f"https://raw.githubusercontent.com/sportsdataverse/cfbfastR-data/main/schedules/csv/cfb_schedules_{SEASON}.csv"
OUT = os.path.join(os.path.dirname(__file__), "..", "site", "records.json")
ALIAS = {"App State": "Appalachian State", "Florida International": "FIU", "Hawai'i": "Hawaii",
         "Massachusetts": "UMass", "San José State": "San Jose State", "UL Monroe": "Louisiana-Monroe"}
nm = lambda t: ALIAS.get(t, t)

def num(x):
    try: return int(float(x))
    except (TypeError, ValueError): return None

with urllib.request.urlopen(URL, timeout=60) as r:
    rows = list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))
rows.sort(key=lambda r: r["start_date"])

games, rec, last = {}, {}, None
for r in rows:
    hp, ap = num(r["home_points"]), num(r["away_points"])
    done = r["completed"] == "TRUE" and hp is not None and ap is not None
    if not done: hp = ap = None
    site = "N" if r["neutral_site"] == "TRUE" else None
    if done: last = r
    for t, o, s, pf, pa, div in ((r["home_team"], r["away_team"], site or "H", hp, ap, r["home_division"]),
                                 (r["away_team"], r["home_team"], site or "A", ap, hp, r["away_division"])):
        if div != "fbs": continue
        t = nm(t)
        games.setdefault(t, []).append([int(r["week"]), nm(o), s, pf, pa])
        if pf is not None:
            w, l = rec.get(t, (0, 0))
            rec[t] = (w + (pf > pa), l + (pf < pa))

if last:
    dt = datetime.fromisoformat(last["start_date"].replace("Z", "+00:00")).astimezone(timezone.utc) - timedelta(hours=8)
    as_of = f"{dt:%b} {dt.day}, {dt.year} (Week {last['week']})"
else:
    as_of = "Season not started"

out = {"asOf": as_of, "rec": {t: f"{w}-{l}" for t, (w, l) in sorted(rec.items())}, "games": games}
if len(games) < 100:
    sys.exit(f"Only {len(games)} FBS teams found; refusing to overwrite records.json")
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
print(f"{as_of}: {len(games)} teams")
