"""Read xtracker.polymarket.com (resolution source for post-count brackets).

Usage:
  python3 strategy/tools/xtracker.py user <handle>      list tracking periods
  python3 strategy/tools/xtracker.py series <tracking_id>
      cumulative + hourly `daily` counts, oldest first, in the exact
      comma-separated form strategy/tools/count_boot.py takes, plus the
      first hour-of-day it needs.

Added 2026-10-08 22:4xZ: WebFetch's summariser mis-transcribed the hourly
series (151 entries reported, 153 values returned, hours skipped), so the
series must come from the API, not a model paraphrase.
"""
import json
import sys
import urllib.request

BASE = "https://xtracker.polymarket.com/api"


def get(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    return d.get("data", d) if isinstance(d, dict) else d


def main(argv):
    if argv[0] == "user":
        d = get(f"/users/{argv[1]}?platform=x&stats=true")
        for t in d.get("trackings", []):
            print(t.get("id"), t.get("startDate"), t.get("endDate"), t.get("title"))
        return
    d = get(f"/trackings/{argv[1]}?includeStats=true")
    st = d.get("stats", {})
    daily = st.get("daily", [])
    print(d.get("title"), d.get("startDate"), d.get("endDate"))
    print({k: v for k, v in st.items() if k != "daily"})
    if not daily:
        return
    first, last = daily[0], daily[-1]
    print(f"entries={len(daily)} first={first} last={last}")
    key = "count" if "count" in first else next(k for k, v in first.items() if isinstance(v, int))
    stamp = next(k for k, v in first.items() if isinstance(v, str))
    print("first_hod", int(first[stamp][11:13]))
    print("sum", sum(int(x.get(key, 0)) for x in daily))
    print(",".join(str(int(x.get(key, 0))) for x in daily))


if __name__ == "__main__":
    main(sys.argv[1:])
