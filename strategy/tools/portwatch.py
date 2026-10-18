"""PortWatch chokepoint daily transits + rolling N-day sums (validated feed: PortWatch chokepoints).

Weekly-total families (e.g. "Will 20-24 ships transit the Strait of Hormuz between Oct 12-18?")
resolve on the SUM of daily n_total over the window; Bab el-Mandeb month-end sets resolve on the
7-day MA. Publication lags several days, so print the latest row date before pricing.

Usage: python3 strategy/tools/portwatch.py PORTNAME_LIKE START_DATE [--window 7] [--edges 20,25,30,35]
  e.g. python3 strategy/tools/portwatch.py Hormuz 2026-08-15
"""
import argparse
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone

LAYER = ("https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/"
         "Daily_Chokepoints_Data/FeatureServer/0/query")

p = argparse.ArgumentParser()
p.add_argument("port")
p.add_argument("start")
p.add_argument("--window", type=int, default=7)
p.add_argument("--edges", default="20,25,30,35")
a = p.parse_args()

q = {"where": f"portname like '%{a.port}%' and date >= DATE '{a.start}'",
     "outFields": "date,portname,n_total,n_tanker", "orderByFields": "date",
     "resultRecordCount": 2000, "f": "json"}
with urllib.request.urlopen(LAYER + "?" + urllib.parse.urlencode(q), timeout=30) as r:
    feats = json.load(r)["features"]
rows = []
for f in feats:
    at = f["attributes"]
    d = at["date"]
    if isinstance(d, (int, float)):
        d = datetime.fromtimestamp(d / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
    rows.append((str(d)[:10], at["n_total"]))
for d, n in rows[-14:]:
    print(d, n)
print("rows", len(rows), "latest", rows[-1][0] if rows else None)
vals = [n for _, n in rows]
w = a.window
sums = [sum(vals[i:i + w]) for i in range(len(vals) - w + 1)]
if sums:
    edges = [int(x) for x in a.edges.split(",")]
    labels = [f"<{edges[0]}"] + [f"{lo}-{hi - 1}" for lo, hi in zip(edges, edges[1:])] + [f"{edges[-1]}+"]
    counts = dict.fromkeys(labels, 0)
    for s in sums:
        i = sum(s >= e for e in edges)
        counts[labels[i]] += 1
    print(f"{w}-day sums: n={len(sums)} min={min(sums)} max={max(sums)} mean={sum(sums) / len(sums):.1f}")
    print("last 10 sums", sums[-10:])
    print("bucket freq", {k: round(v / len(sums), 3) for k, v in counts.items()})
