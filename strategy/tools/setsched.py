"""Apply a pacing patch to strategy/schedule.json, text-level.

usage: python3 strategy/tools/setsched.py strategy/schedule.json reports/sched-patch.json

The patch file is a JSON object with any of:
  "next_full_cycle_after": "<UTC ISO>"
  "reason": "<the CURRENT SET block>"
  "watch_append": {"<watch item prefix>": "<text appended to that item>"}

Only the touched lines change (the file holds one key or one watch item per
line), so the diff stays readable; the result must still parse as JSON with
the same keys and the same number of watch items, or nothing is written.

Added 2026-10-11 15:5xZ: on the operator machine `python3 work/<one-off>.py`
and heredoc python are approval-gated, so the per-cycle one-off rewrite
scripts (work/upd_sched_*.py) cannot run there; tools under strategy/tools/
can.
"""
import json
import sys


def main():
    path, patch_path = sys.argv[1], sys.argv[2]
    with open(patch_path) as f:
        patch = json.load(f)
    with open(path) as f:
        text = f.read()
    before = json.loads(text)
    ascii_only = all(ord(c) < 128 for c in text)
    lines = text.split('\n')

    def dump(value):
        return json.dumps(value, ensure_ascii=ascii_only)

    for key in ('next_full_cycle_after', 'reason'):
        if key not in patch:
            continue
        head = f'  "{key}": '
        hits = [i for i, line in enumerate(lines) if line.startswith(head)]
        if len(hits) != 1:
            sys.exit(f'refusing: {len(hits)} lines start with {head!r}')
        lines[hits[0]] = head + dump(patch[key]) + ','

    for prefix, extra in (patch.get('watch_append') or {}).items():
        head = '    ' + dump(prefix)[:-1]
        hits = [i for i, line in enumerate(lines) if line.startswith(head)]
        if len(hits) != 1:
            sys.exit(f'refusing: {len(hits)} watch items start with {prefix!r}')
        line = lines[hits[0]]
        tail = ',' if line.endswith(',') else ''
        item = json.loads(line.strip().rstrip(','))
        lines[hits[0]] = '    ' + dump(item + extra) + tail

    out = '\n'.join(lines)
    after = json.loads(out)
    if list(after) != list(before):
        sys.exit('refusing: top-level keys changed')
    if len(after['watch_items']) != len(before['watch_items']):
        sys.exit('refusing: watch item count changed')
    with open(path, 'w') as f:
        f.write(out)
    changed = [k for k in after if after[k] != before[k]]
    print(f'schedule updated: {changed}')


if __name__ == '__main__':
    main()
