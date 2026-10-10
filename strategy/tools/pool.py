"""Look up scan-pool rows by market id or by case-insensitive question substring.

Usage: python3 core/scan.py --hours 336 --limit 800 > work/scan-pool.json
       python3 strategy/tools/pool.py [--desc N] [--file PATH] <id-or-substring> [...]

Prints id, question, end date, event, outcome prices, liquidity, token ids and
the first N characters of the description (default 600, 0 to hide it).
"""
import argparse
import json

p = argparse.ArgumentParser()
p.add_argument("keys", nargs="+")
p.add_argument("--desc", type=int, default=600)
p.add_argument("--file", default="work/scan-pool.json")
a = p.parse_args()

rows = [json.loads(line) for line in open(a.file) if line.strip()]
for k in a.keys:
    hits = [r for r in rows if r["market_id"] == k or (not k.isdigit() and k.lower() in r["question"].lower())]
    for r in hits:
        print(f"{r['market_id']} | {r['question']} | end {r['end_date']} | ev {r.get('event_id')} {r.get('event_slug')}")
        print(f"   outcomes {r['outcomes']} prices {r['outcome_prices']} liq {r['liquidity']:.0f} vol24 {r['volume_24h']:.0f}")
        print(f"   tokens {r['clob_token_ids']}")
        if a.desc:
            print("   desc:", r.get("description", "")[: a.desc].replace("\n", " "))
    if not hits:
        print(f"-- no hit for {k}")
