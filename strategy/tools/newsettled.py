"""List forecasts that settled in the working tree but were open at HEAD.

usage: python3 strategy/tools/newsettled.py [--rev HEAD]

Added 2026-10-15: settled.py filters on settled_ts, which is the market's
resolution time, not the time resolve.py ran. After a 4-day runner gap the
2026-10-15 20:4xZ resolve.py settled 128 forecasts whose settled_ts all sat
on Oct 12-14, and `settled.py 2026-10-15T20:00` printed nothing. Diffing
against the last commit is the reliable "what did this tick settle" view.
Prints one line per row (S = superseded, - = the final row on that market),
then dBrier sums by skip reason and category over the final rows only.
"""
import argparse
import json
import subprocess
from collections import defaultdict


def load(text):
    out = {}
    for line in text.splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        out[d.get('id')] = d
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rev', default='HEAD')
    a = ap.parse_args()
    old = load(subprocess.run(['git', 'show', a.rev + ':journal/forecasts.jsonl'],
                              capture_output=True, text=True).stdout)
    new = load(open('journal/forecasts.jsonl').read())
    rows = [d for k, d in new.items() if d.get('status') in ('won', 'lost')
            and old.get(k, {}).get('status') not in ('won', 'lost')]
    rows.sort(key=lambda d: (d.get('market_id') or '', d.get('ts') or ''))
    by_skip = defaultdict(lambda: [0, 0.0])
    by_cat = defaultdict(lambda: [0, 0.0])
    tot = {'S': [0, 0.0], '-': [0, 0.0]}
    for d in rows:
        p = d['est_prob']
        m = d.get('market_prob_at_record')
        y = 1.0 if d['status'] == 'won' else 0.0
        db = (p - y) ** 2 - ((m - y) ** 2 if m is not None else 0.0)
        sup = 'S' if d.get('superseded_by') else '-'
        tot[sup][0] += 1
        tot[sup][1] += db
        if sup == '-':
            for agg, key in ((by_skip, d.get('skip_reason')), (by_cat, d.get('category'))):
                agg[key][0] += 1
                agg[key][1] += db
        print(f"{d['id']} {d['ts'][5:16]} m{d.get('market_id')} {sup} {d['outcome'][:10]:10} "
              f"est={p:.2f} mid={m} bid={d.get('best_bid_at_record')} ask={d.get('best_ask_at_record')} "
              f"{d['status']:4} dB={db:+.4f} {d.get('category')} [{d.get('skip_reason')}] | {d['question'][:85]}")
    print()
    print(f"n={len(rows)} final={tot['-'][0]} sum_dB={tot['-'][1]:+.4f} "
          f"superseded={tot['S'][0]} sum_dB={tot['S'][1]:+.4f}")
    for title, agg in (('by skip (final rows)', by_skip), ('by category (final rows)', by_cat)):
        print(title + ':')
        for k, v in sorted(agg.items(), key=lambda kv: -kv[1][0]):
            print(f"  {k}: n={v[0]} sum_dB={v[1]:+.4f} mean={v[1] / v[0]:+.4f}")


if __name__ == '__main__':
    main()
