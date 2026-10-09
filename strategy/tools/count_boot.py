#!/usr/bin/env python3
"""Sliding-window bootstrap for post-count brackets.

Usage: python3 strategy/tools/count_boot.py <hours_left> <lo_add> <hi_add> <first_hod> <counts>
  counts     comma-separated hourly counts for the period so far (xtracker
             `daily` series, oldest first)
  first_hod  UTC hour-of-day of the first count
  lo_add/hi_add  inclusive range of ADDITIONAL posts that lands the bracket

Prints P(lo_add <= additional <= hi_add) over every sliding window of
<hours_left> hours (all), over windows starting at the same hour-of-day as
now (aligned), and over windows inside the last 72h (recent). Per the
2026-09-25 retro, record the aligned figure when n>=20, else all; recency
views go in the note only.
"""
import sys


def main(argv):
    hours_left, lo, hi, first_hod = (int(a) for a in argv[:4])
    h = [int(x) for x in argv[4].split(",")]
    n = len(h)
    sums = [sum(h[i:i + hours_left]) for i in range(n - hours_left + 1)]
    if not sums:
        sys.exit("series shorter than hours_left")
    hit = lambda s: lo <= s <= hi  # noqa: E731
    now_hod = (first_hod + n) % 24
    aligned = [s for i, s in enumerate(sums) if (first_hod + i) % 24 == now_hod]
    # window starts in the last 72h of the series; when hours_left > 72 no
    # window fits there, so fall back to the latest window (fixed 2026-10-09:
    # slicing by n instead of len(sums) gave an empty list and a crash).
    recent = sums[max(0, n - 72):] or sums[-1:]
    print(f"total so far={sum(h)} hours observed={n} now_hod={now_hod}")
    print(f"all     n={len(sums)} P={sum(map(hit, sums)) / len(sums):.3f} "
          f"mean_add={sum(sums) / len(sums):.1f} max_add={max(sums)}")
    if aligned:
        print(f"aligned n={len(aligned)} sums={aligned} "
              f"P={sum(map(hit, aligned)) / len(aligned):.3f}")
    print(f"recent  n={len(recent)} P={sum(map(hit, recent)) / len(recent):.3f}")


if __name__ == "__main__":
    main(sys.argv[1:])
