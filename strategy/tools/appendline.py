"""Append one JSON object, read from a file, as a single line to a JSONL file.

usage: python3 strategy/tools/appendline.py strategy/funnel.jsonl reports/row.json
       python3 strategy/tools/appendline.py --text journal/cycles.log reports/line.txt

Validates the JSON first so a malformed row never lands in the target.
--text appends the source's first line verbatim (for cycles.log), refusing
multi-line input because each cycle writes ONE log line.
"""
import json
import sys


def main():
    args = sys.argv[1:]
    text = args[0] == '--text'
    if text:
        args = args[1:]
    target, src = args[0], args[1]
    with open(src) as f:
        if text:
            lines = f.read().strip('\n').split('\n')
            if len(lines) != 1:
                sys.exit(f'refusing: {len(lines)} lines in {src}, expected 1')
            out = lines[0]
        else:
            out = json.dumps(json.load(f), ensure_ascii=False)
    with open(target, 'a') as f:
        f.write(out + '\n')
    print(f'appended 1 line to {target}')


if __name__ == '__main__':
    main()
