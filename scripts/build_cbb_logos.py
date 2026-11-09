#!/usr/bin/env python3
"""Scans site/cbb-logos/ and writes site/cbb-logos.json (team -> image file).
A filename only needs to START with the team name or a common nickname, e.g.
"Duke.png", "kansas-jayhawks.svg", "UConn.png", "St. John's.png"."""
import json, os, re, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "site")
LOGOS = os.path.join(SITE, "cbb-logos")
EXT = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}
NICK = {"Connecticut": "UConn", "Pitt": "Pittsburgh", "UNC": "North Carolina", "Mississippi": "Ole Miss",
        "Miami Ohio": "Miami (OH)", "Miami RedHawks": "Miami (OH)", "Miami FL": "Miami", "Miami Florida": "Miami",
        "Cal": "California", "LSU": "LSU", "Louisiana State": "LSU", "VCU": "VCU", "UCSB": "UC Santa Barbara",
        "UNLV": "UNLV", "FAU": "Florida Atlantic", "FGCU": "Florida Gulf Coast", "UMBC": "UMBC",
        "Hawaii": "Hawai'i", "Massachusetts": "UMass", "Texas AM": "Texas A&M", "TAMU": "Texas A&M",
        "NC State": "NC State", "North Carolina State": "NC State", "SMU": "SMU", "TCU": "TCU", "BYU": "BYU"}
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

with open(os.path.join(SITE, "cbb-data.json"), encoding="utf-8") as fh:
    TEAMS = [t for v in json.load(fh)["confs"].values() for t in v]
known = set(TEAMS)
keys = []
for t in TEAMS:
    keys.append((norm(t), t))
    if t.endswith(" State"): keys.append((norm(t[:-6] + " St"), t))
    if t.startswith("St. "): keys.append((norm("Saint " + t[4:]), t))
    if t.startswith("Saint "): keys.append((norm("St. " + t[6:]), t))
    if "'" in t: keys.append((norm(t.replace("'", "")), t))
for a, t in NICK.items():
    if t in known: keys.append((norm(a), t))

out, unmatched = {}, []
for f in sorted(os.listdir(LOGOS)) if os.path.isdir(LOGOS) else []:
    stem, ext = os.path.splitext(f)
    if ext.lower() not in EXT: continue
    b = norm(stem)
    cand = [k for k in keys if b.startswith(k[0])]
    if not cand:
        unmatched.append(f); continue
    team = max(cand, key=lambda k: len(k[0]))[1]
    if team in out:
        print(f"Duplicate logo for {team}: keeping {out[team]}, ignoring {f}"); continue
    out[team] = "cbb-logos/" + urllib.parse.quote(f)

with open(os.path.join(SITE, "cbb-logos.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
print(f"{len(out)} team logos matched")
for f in unmatched: print(f"UNMATCHED (rename so it starts with the team name): {f}")
print(f"{len(TEAMS) - len(out)} teams still using the jersey")
