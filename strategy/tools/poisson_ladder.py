"""Poisson bracket probabilities for a count ladder given the count so far.

Usage: python3 strategy/tools/poisson_ladder.py OBSERVED DAYS_LEFT RATE_PER_DAY [RATE ...]
        [--low 6] [--high 13]
Prints P(final <= low), P(final == k) for low<k<=high, P(final > high) per rate.
"""
import argparse
from math import exp, factorial

p = argparse.ArgumentParser()
p.add_argument("observed", type=int)
p.add_argument("days_left", type=float)
p.add_argument("rates", type=float, nargs="+")
p.add_argument("--low", type=int, default=6)
p.add_argument("--high", type=int, default=13)
a = p.parse_args()

for r in a.rates:
    m = r * a.days_left
    pk = [exp(-m) * m**k / factorial(k) for k in range(a.high + 40)]
    add = lambda total: pk[total - a.observed] if total >= a.observed else 0.0
    le = sum(add(t) for t in range(0, a.low + 1))
    mids = {k: add(k) for k in range(a.low + 1, a.high + 1)}
    gt = 1 - le - sum(mids.values())
    cells = " ".join(f"{k}:{v:.3f}" for k, v in mids.items())
    print(f"rate {r:.3f}/d mean_add {m:.2f}  <={a.low}:{le:.3f} {cells} >{a.high}:{gt:.3f}")
