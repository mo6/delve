#!/usr/bin/env python3
"""Print a Markdown table of issues sorted by effort, low to high.

    python tools/effort_table.py                    # proposed issues (the common case)
    python tools/effort_table.py --status all        # every issue, any status
    python tools/effort_table.py --status proposed,in-progress

Columns are Effort, ID, Type, Created, Updated, Title, read straight from each issue's front
matter (the same fields `tools/issues.py` already parses). Not part of the delve package and not
imported by it, exactly like `screens.py` and `issues.py`.
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from issues import load  # noqa: E402  (path set up above)

EFFORT_ORDER = {'low': 0, 'medium': 1, 'high': 2}


def build_table(records, statuses):
    rows = []
    for _path, meta in records:
        if not meta:
            continue
        if statuses is not None and meta.get('status') not in statuses:
            continue
        rows.append(meta)

    rows.sort(key=lambda m: (
        EFFORT_ORDER.get(m.get('effort'), len(EFFORT_ORDER)),
        m.get('created', ''),
        m.get('id', ''),
    ))

    lines = ['| Effort | ID | Type | Created | Updated | Title |',
             '|---|---|---|---|---|---|']
    for m in rows:
        lines.append('| {effort} | {id} | {type} | {created} | {updated} | {title} |'.format(
            effort=m.get('effort') or '-',
            id=m.get('id', '?'),
            type=m.get('type') or '-',
            created=m.get('created') or '-',
            updated=m.get('updated') or '-',
            title=m.get('title', ''),
        ))
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--status', default='proposed',
                     help="comma-separated statuses to include, or 'all' (default: proposed)")
    args = ap.parse_args(argv)

    statuses = None if args.status == 'all' else {s.strip() for s in args.status.split(',')}

    records = load()
    print(build_table(records, statuses))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
