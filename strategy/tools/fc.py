"""Print compact forecast rows by forecast id, market id or question substring.

Usage: python3 strategy/tools/fc.py [--note N] <id-or-market-id-or-substring> [...]
       python3 strategy/tools/fc.py --anchor-audit [--tol 0.02]

Added 2026-10-11 12:2xZ: forecasts.jsonl rows are longer than the search
tool prints ("Omitted long matching line"), so a cycle could not read the
market id or category of a row it was about to supersede.

--anchor-audit (RETRO-20261109-2110): lists OPEN ai-model-release forecasts
whose est_prob sits more than --tol off the mid at record. Under the playbook
"AI release-date anchoring rule", each one is a breach unless its note cites a
POSITIVE primary source. Three such breaches on the Fable 5.2+ ladder
(cd72944f6d07, 091c61d2f40d, eb80da59dbd6) settled Yes on 2026-11-09 for a
summed dBrier of +0.865. Run it at the forecast step of any FULL cycle that
touched the category.
"""
import argparse
import json

p = argparse.ArgumentParser()
p.add_argument("keys", nargs="*")
p.add_argument("--note", type=int, default=160)
p.add_argument("--anchor-audit", action="store_true")
p.add_argument("--tol", type=float, default=0.02)
a = p.parse_args()

rows = []
for line in open("journal/forecasts.jsonl"):
    try:
        rows.append(json.loads(line))
    except ValueError:
        continue


def show(r):
    print(f"{r.get('id')} {r.get('ts')} mkt {r.get('market_id')} {r.get('outcome')} est {r.get('est_prob')} "
          f"mid {r.get('market_prob_at_record')} cat {r.get('category')} skip {r.get('skip_reason')} "
          f"end {r.get('end_date')} | {r.get('question')} | {(r.get('note') or '')[:a.note]}")


if a.anchor_audit:
    n = 0
    for r in rows:
        if r.get("category") != "ai-model-release" or r.get("status") not in (None, "open"):
            continue
        est, mid = r.get("est_prob"), r.get("market_prob_at_record")
        if est is None or mid is None or abs(est - mid) <= a.tol:
            continue
        n += 1
        print(f"BREACH? |est-mid|={abs(est - mid):.3f}  ", end="")
        show(r)
    print(f"-- anchor audit: {n} open ai-model-release row(s) off the mid by > {a.tol}")
elif not a.keys:
    p.error("give keys or --anchor-audit")

for k in a.keys:
    hits = [r for r in rows if k in (r.get("id"), r.get("market_id"))
            or (not k.isdigit() and len(k) > 12 and k.lower() in r.get("question", "").lower())]
    for r in hits:
        show(r)
    if not hits:
        print(f"-- no hit for {k}")
