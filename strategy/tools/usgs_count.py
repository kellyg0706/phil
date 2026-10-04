"""Count USGS M>=min_mag events in a UTC window (validated-feed family: USGS weekly counts).

Usage: python3 strategy/tools/usgs_count.py START_ISO [END_ISO] [--min-mag 5.5]
"""
import argparse
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

p = argparse.ArgumentParser()
p.add_argument("start")
p.add_argument("end", nargs="?")
p.add_argument("--min-mag", type=float, default=5.5)
a = p.parse_args()

q = {"format": "geojson", "starttime": a.start, "minmagnitude": a.min_mag, "orderby": "time-asc"}
if a.end:
    q["endtime"] = a.end
url = "https://earthquake.usgs.gov/fdsnws/event/1/query?" + urllib.parse.urlencode(q)
with urllib.request.urlopen(url, timeout=30) as r:
    d = json.load(r)
for f in d["features"]:
    pr = f["properties"]
    t = datetime.fromtimestamp(pr["time"] / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"{t}  M{pr['mag']}  {pr['place']}")
print("count", len(d["features"]))
