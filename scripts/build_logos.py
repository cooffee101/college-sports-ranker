#!/usr/bin/env python3
"""Scans site/logos/ and writes site/logos.json, which tells the page which
image file belongs to which team. Filenames just need to START with the team
name or a common nickname (e.g. "Ohio State.png", "ohio-state-buckeyes.svg",
"Pitt.png"). Runs automatically in the GitHub Actions workflow."""
import json, os, re, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "site")
LOGOS = os.path.join(SITE, "logos")
EXT = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}
TEAMS = ["Boston College", "California", "Clemson", "Duke", "Florida State", "Georgia Tech", "Louisville", "Miami", "NC State", "North Carolina", "Pittsburgh", "SMU", "Stanford", "Syracuse", "Virginia", "Virginia Tech", "Wake Forest", "Army", "Charlotte", "East Carolina", "Florida Atlantic", "Memphis", "Navy", "North Texas", "Rice", "South Florida", "Temple", "Tulane", "Tulsa", "UAB", "UTSA", "Arizona", "Arizona State", "Baylor", "BYU", "Cincinnati", "Colorado", "Houston", "Iowa State", "Kansas", "Kansas State", "Oklahoma State", "TCU", "Texas Tech", "UCF", "Utah", "West Virginia", "Illinois", "Indiana", "Iowa", "Maryland", "Michigan", "Michigan State", "Minnesota", "Nebraska", "Northwestern", "Ohio State", "Oregon", "Penn State", "Purdue", "Rutgers", "UCLA", "USC", "Washington", "Wisconsin", "Delaware", "FIU", "Jacksonville State", "Kennesaw State", "Liberty", "Middle Tennessee", "Missouri State", "New Mexico State", "Sam Houston", "Western Kentucky", "Akron", "Ball State", "Bowling Green", "Buffalo", "Central Michigan", "Eastern Michigan", "Kent State", "Miami (OH)", "Ohio", "Sacramento State", "Toledo", "UMass", "Western Michigan", "Air Force", "Hawaii", "Nevada", "New Mexico", "North Dakota State", "Northern Illinois", "San Jose State", "UNLV", "UTEP", "Wyoming", "Boise State", "Colorado State", "Fresno State", "Oregon State", "San Diego State", "Texas State", "Utah State", "Washington State", "Alabama", "Arkansas", "Auburn", "Florida", "Georgia", "Kentucky", "LSU", "Mississippi State", "Missouri", "Oklahoma", "Ole Miss", "South Carolina", "Tennessee", "Texas", "Texas A&M", "Vanderbilt", "Appalachian State", "Arkansas State", "Coastal Carolina", "Georgia Southern", "Georgia State", "James Madison", "Louisiana", "Louisiana Tech", "Louisiana-Monroe", "Marshall", "Old Dominion", "South Alabama", "Southern Miss", "Troy", "Notre Dame", "UConn"]
NICK = {
 "Pitt": "Pittsburgh",
 "App State": "Appalachian State",
 "Appalachian": "Appalachian State",
 "Massachusetts": "UMass",
 "Connecticut": "UConn",
 "ULM": "Louisiana-Monroe",
 "UL Monroe": "Louisiana-Monroe",
 "Louisiana Monroe": "Louisiana-Monroe",
 "UL Lafayette": "Louisiana",
 "Louisiana Lafayette": "Louisiana",
 "NDSU": "North Dakota State",
 "Mississippi": "Ole Miss",
 "San Jose": "San Jose State",
 "SJSU": "San Jose State",
 "SDSU": "San Diego State",
 "FAU": "Florida Atlantic",
 "Florida International": "FIU",
 "UCF": "UCF",
 "Central Florida": "UCF",
 "USF": "South Florida",
 "Southern Mississippi": "Southern Miss",
 "TAMU": "Texas A&M",
 "Texas AM": "Texas A&M",
 "Louisiana State": "LSU",
 "UNC": "North Carolina",
 "UNC Charlotte": "Charlotte",
 "North Carolina State": "NC State",
 "Cal": "California",
 "WKU": "Western Kentucky",
 "MTSU": "Middle Tennessee",
 "ODU": "Old Dominion",
 "JMU": "James Madison",
 "FSU": "Florida State",
 "ECU": "East Carolina",
 "WVU": "West Virginia",
 "BGSU": "Bowling Green",
 "CMU": "Central Michigan",
 "EMU": "Eastern Michigan",
 "WMU": "Western Michigan",
 "NIU": "Northern Illinois",
 "UNM": "New Mexico",
 "NMSU": "New Mexico State",
 "ASU": "Arizona State",
 "GSU": "Georgia State",
 "TTU": "Texas Tech",
 "OU": "Oklahoma",
 "UGA": "Georgia",
 "PSU": "Penn State",
 "Miami Ohio": "Miami (OH)",
 "Miami RedHawks": "Miami (OH)",
 "Miami Florida": "Miami",
 "Miami FL": "Miami",
 "Hawai'i": "Hawaii",
 "Sam Houston State": "Sam Houston",
 "Louisiana Ragin Cajuns": "Louisiana",
 "Army Black Knights": "Army",
 "Sacramento": "Sacramento State"
}
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())

keys = []
for t in TEAMS:
    keys.append((norm(t), t))
    if t.endswith(" State"):
        keys.append((norm(t[:-6] + " St"), t))
for a, t in NICK.items():
    keys.append((norm(a), t))

out, unmatched = {}, []
files = sorted(os.listdir(LOGOS)) if os.path.isdir(LOGOS) else []
for f in files:
    stem, ext = os.path.splitext(f)
    if ext.lower() not in EXT:
        continue
    b = norm(stem)
    cand = [k for k in keys if b.startswith(k[0])]
    if not cand:
        unmatched.append(f)
        continue
    team = max(cand, key=lambda k: len(k[0]))[1]
    if team in out:
        print(f"Duplicate logo for {team}: keeping {out[team]}, ignoring {f}")
        continue
    out[team] = "logos/" + urllib.parse.quote(f)

with open(os.path.join(SITE, "logos.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
print(f"{len(out)} team logos matched")
for f in unmatched:
    print(f"UNMATCHED (rename so it starts with the team name): {f}")
missing = [t for t in TEAMS if t not in out]
print(f"{len(missing)} teams still using the helmet")
