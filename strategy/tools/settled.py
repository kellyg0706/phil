"""List forecasts settled at or after a UTC timestamp, for retro writing.

usage: python3 strategy/tools/settled.py 2026-10-06T23:40
"""
import json
import sys

FIELDS = ('id', 'ts', 'market_id', 'question', 'outcome', 'est_prob',
          'market_prob_at_record', 'best_bid_at_record', 'best_ask_at_record',
          'category', 'skip_reason', 'status', 'outcome_won', 'settled_ts',
          'supersedes', 'note')


def main():
    since = sys.argv[1]
    with open('journal/forecasts.jsonl') as f:
        for line in f:
            d = json.loads(line)
            if d.get('settled_ts', '') >= since:
                print(json.dumps({k: d.get(k) for k in FIELDS}))
                print()


if __name__ == '__main__':
    main()
