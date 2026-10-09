#!/usr/bin/env python3
"""Annualized close-to-close realized vol from a comma-separated close list.

Feeds touch.py's --ann-vol with a measured number. Use --drop-abs to
exclude jump days (earnings gaps) from the diffusion estimate and report
how many were dropped.

  python3 strategy/tools/rvol.py --closes "146.89,148.62,..." [--last 20] [--drop-abs 0.08]
"""
import argparse
import json
import math


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--closes", required=True)
    ap.add_argument("--last", type=int, default=0, help="use only the last N returns")
    ap.add_argument("--drop-abs", type=float, default=0.0,
                    help="drop log returns with |r| above this (jump days)")
    ap.add_argument("--year-days", type=float, default=252.0)
    a = ap.parse_args()
    closes = [float(x) for x in a.closes.split(",") if x.strip()]
    rets = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    if a.last:
        rets = rets[-a.last:]
    dropped = [r for r in rets if a.drop_abs and abs(r) > a.drop_abs]
    kept = [r for r in rets if not (a.drop_abs and abs(r) > a.drop_abs)]
    n = len(kept)
    mean = sum(kept) / n
    var = sum((r - mean) ** 2 for r in kept) / (n - 1)
    sd = math.sqrt(var)
    print(json.dumps({
        "n_returns": n,
        "dropped": [round(r, 4) for r in dropped],
        "daily_sd": round(sd, 5),
        "ann_vol": round(sd * math.sqrt(a.year_days), 4),
    }))


if __name__ == "__main__":
    main()
