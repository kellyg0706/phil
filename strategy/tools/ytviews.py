"""Dated YouTube view-count reads for the video-views bracket family.

Usage: python3 strategy/tools/ytviews.py <video_id> [--channel <channel_id>]

Prints one line per source that answered, each stamped with the read time:
  watch  - viewCount from the watch page's embedded player JSON (live counter)
  ryd    - returnyoutubedislikeapi mirror (lags YouTube by an unknown amount)
  rss    - channel feed media:statistics (only with --channel; lags, and the
           entry's <updated> stamp is not the time of the count)
Two `watch` reads some minutes apart give the pace; never mix sources for a
pace, their lags differ (funnel rows 2026-09-26 and 2026-10-09: RYD read below
an older RSS read on the same video).
"""
import argparse
import json
import re
import urllib.request
from datetime import datetime, timezone

UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": "CONSENT=YES+1",
}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


p = argparse.ArgumentParser()
p.add_argument("video_id")
p.add_argument("--channel")
p.add_argument("--poll", type=int, default=0, help="extra watch reads after the first")
p.add_argument("--interval", type=float, default=30.0, help="seconds between polled reads")
a = p.parse_args()

if a.poll:
    # The public counter moves in steps (2026-10-10: +13 over 4 min, then +45k
    # inside 100 s), so a pace needs a window that spans several steps.
    import time

    first = last = None
    for i in range(a.poll + 1):
        try:
            m = re.search(r'"viewCount":"(\d+)"', get(f"https://www.youtube.com/watch?v={a.video_id}"))
            v = int(m.group(1)) if m else None
        except Exception as e:
            v = None
            print(f"{now()} watch error {e}", flush=True)
        if v is not None:
            t = time.time()
            if first is None:
                first = (t, v)
            if last is None or v != last[1]:
                print(f"{now()} watch {v:,}" + (f" step {v - last[1]:+,}" if last else ""), flush=True)
            last = (t, v)
        if i < a.poll:
            time.sleep(a.interval)
    if first and last and last[0] > first[0]:
        hrs = (last[0] - first[0]) / 3600
        print(f"{now()} window {hrs * 60:.1f} min, {last[1] - first[1]:+,} views, {(last[1] - first[1]) / hrs:,.0f}/h")
    raise SystemExit

try:
    html = get(f"https://www.youtube.com/watch?v={a.video_id}")
    m = re.search(r'"viewCount":"(\d+)"', html)
    d = re.search(r'"publishDate":"([^"]+)"', html)
    if m:
        print(f"{now()} watch {int(m.group(1)):,} publishDate {d.group(1) if d else '?'}")
    else:
        print(f"{now()} watch no viewCount in page ({len(html)} bytes)")
except Exception as e:
    print(f"{now()} watch error {e}")

try:
    j = json.loads(get(f"https://returnyoutubedislikeapi.com/votes?videoId={a.video_id}"))
    print(f"{now()} ryd {j['viewCount']:,} dateCreated {j.get('dateCreated')}")
except Exception as e:
    print(f"{now()} ryd error {e}")

if a.channel:
    try:
        xml = get(f"https://www.youtube.com/feeds/videos.xml?channel_id={a.channel}")
        for entry in xml.split("<entry>")[1:]:
            if f"<yt:videoId>{a.video_id}</yt:videoId>" in entry:
                v = re.search(r'<media:statistics views="(\d+)"', entry)
                u = re.search(r"<updated>([^<]+)</updated>", entry)
                pub = re.search(r"<published>([^<]+)</published>", entry)
                print(f"{now()} rss {int(v.group(1)):,} published {pub.group(1)} entry-updated {u.group(1)}")
    except Exception as e:
        print(f"{now()} rss error {e}")
