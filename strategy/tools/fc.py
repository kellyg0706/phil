"""Print compact forecast rows by forecast id, market id or question substring.

Usage: python3 strategy/tools/fc.py [--note N] <id-or-market-id-or-substring> [...]

Added 2026-10-11 12:2xZ: forecasts.jsonl rows are longer than the search
tool prints ("Omitted long matching line"), so a cycle could not read the
market id or category of a row it was about to supersede.
"""
import argparse
import json

p = argparse.ArgumentParser()
p.add_argument("keys", nargs="+")
p.add_argument("--note", type=int, default=160)
a = p.parse_args()

rows = []
for line in open("journal/forecasts.jsonl"):
    try:
        rows.append(json.loads(line))
    except ValueError:
        continue
for k in a.keys:
    hits = [r for r in rows if k in (r.get("id"), r.get("market_id"))
            or (not k.isdigit() and len(k) > 12 and k.lower() in r.get("question", "").lower())]
    for r in hits:
        print(f"{r.get('id')} {r.get('ts')} mkt {r.get('market_id')} {r.get('outcome')} est {r.get('est_prob')} "
              f"mid {r.get('market_prob_at_record')} cat {r.get('category')} skip {r.get('skip_reason')} "
              f"end {r.get('end_date')} | {r.get('question')} | {(r.get('note') or '')[:a.note]}")
    if not hits:
        print(f"-- no hit for {k}")
