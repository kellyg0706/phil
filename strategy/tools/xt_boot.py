#!/usr/bin/env python3
"""xtracker series -> count_boot bracket table, in one call.

Usage: python3 strategy/tools/xt_boot.py <target_tracking_id> <history_tracking_id> <hours_left> <lo-hi> [<lo-hi> ...]
  target_tracking_id   the period being forecast (its cumulative is the count so far)
  history_tracking_id  the series the sliding windows are drawn from (the monthly tracker)
  hours_left           whole hours left in the target period
  lo-hi                FINAL-count brackets, inclusive; use 90- for an open top

Added 2026-10-11 18:3xZ: count_boot.py takes the hourly series as one argv
string, and the operator-machine permission gate rejects shell variables and
loops, so a four-bracket read needed four hand-pasted 255-value commands.
Same statistics as count_boot.py (all / aligned / recent windows).
"""
import sys

from xtracker import get


def series(tid):
    d = get(f"/trackings/{tid}?includeStats=true")
    daily = d.get("stats", {}).get("daily", [])
    return d, [int(x.get("count", 0)) for x in daily], int(daily[0]["date"][11:13]) if daily else 0


def main(argv):
    target, hist, hours_left = argv[0], argv[1], int(argv[2])
    td, tcounts, _ = series(target)
    _, h, first_hod = series(hist)
    so_far = sum(tcounts)
    n = len(h)
    sums = [sum(h[i:i + hours_left]) for i in range(n - hours_left + 1)]
    if not sums:
        sys.exit("history shorter than hours_left")
    now_hod = (first_hod + n) % 24
    aligned = [s for i, s in enumerate(sums) if (first_hod + i) % 24 == now_hod]
    recent = sums[max(0, n - 72):] or sums[-1:]
    print(f"{td.get('title')} count so far={so_far} (target hours={len(tcounts)}) "
          f"history hours={n} now_hod={now_hod} hours_left={hours_left}")
    print(f"windows all n={len(sums)} mean_add={sum(sums) / len(sums):.1f} max_add={max(sums)} "
          f"aligned n={len(aligned)} recent n={len(recent)}")
    for b in argv[3:]:
        lo_s, hi_s = b.split("-")
        lo = int(lo_s) - so_far
        hi = (int(hi_s) if hi_s else 10 ** 9) - so_far
        hit = lambda s: lo <= s <= hi  # noqa: E731
        p = lambda xs: sum(map(hit, xs)) / len(xs) if xs else float("nan")  # noqa: E731
        print(f"{b:>8}: needs +{max(lo, 0)}..{hi if hi < 10 ** 8 else 'inf'}  "
              f"all={p(sums):.3f} aligned={p(aligned):.3f} recent={p(recent):.3f}")


if __name__ == "__main__":
    main(sys.argv[1:])
