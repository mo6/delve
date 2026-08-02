#!/usr/bin/env python3
"""Index and lint the issues/ tree.

    python tools/issues.py            # rebuild the index table in issues/README.md
    python tools/issues.py --check    # lint + assert the index is current; write nothing

Not part of the delve package and not imported by it, exactly like tools/screenshot.py. Stdlib
only: the front matter is a small, fixed shape, so it is parsed by hand rather than pulling in
a YAML dependency (the same no-Pydantic, stdlib-only line the issues README states).

What --check enforces, gathering every problem before it exits (so one run reports them all):

  - every DELVE-NNNN-slug.md has the required front-matter keys, and its id matches its filename;
  - ids are unique and contiguous from DELVE-0001;
  - status is one of the known values, and the file sits in the directory that status implies
    (implemented/superseded -> archive/, rejected -> rejected/, proposed/in-progress -> root);
  - implemented/superseded carry >=1 commit; proposed/in-progress/rejected carry none;
  - the optional `type` is a known tier (epic|feature|story|bug), and an optional `epic:` links to a
    real requirement that is itself `type: epic` (so the generated Epics rollup is trustworthy);
  - every listed commit exists in git (skipped when not run inside a work tree), except the
    'pre-reset' sentinel used on every issue archived before the 2026-07-31 history squash;
  - every `assets/...` reference in an issue body names a file that exists next to it, starting
    with that issue's own id (DELVE-NNNN-slug.ext), and every file actually in an `assets/`
    directory is referenced by some issue there (no orphans left behind by a move);
  - a PNG or JPEG asset is at most 800px wide (read from its own header, no library needed);
  - no em-dash anywhere (the repo-wide rule);
  - the generated index block in README.md is up to date.

Exit status is non-zero if any check fails, so it drops straight into ./run-tests.sh.
"""
import argparse
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ISSUES_DIR = ROOT / 'issues'
README = ISSUES_DIR / 'README.md'

REQUIRED_KEYS = ['id', 'title', 'status', 'area', 'version', 'created', 'updated',
                 'commits', 'related', 'supersedes', 'docs']
STATUSES = {'proposed', 'in-progress', 'implemented', 'superseded', 'rejected'}
SHIPPED = {'implemented', 'superseded'}          # these must carry commits
# A commit recorded before the deliberate history squash documented in CLAUDE.md (2026-07-31,
# ahead of first pushing to a remote): the object is gone from git for good, by design, not a
# broken reference to fix. Every pre-squash `commits:` list was rewritten to this one sentinel so
# `implemented`/`superseded`'s "must list at least one commit" rule still holds without claiming a
# hash git can no longer resolve; it is exempt from the existence check below.
PRE_RESET_SENTINEL = 'pre-reset'
# The agile tiers plus 'bug': epic/feature/story are the planned hierarchy (AGILE.md), 'bug' is a
# reported defect that may still hang off an epic like a story does.
TYPES = {'epic', 'feature', 'story', 'bug'}
# How much work an LLM coding agent would need (AGILE.md); required while proposed/in-progress,
# not backfilled onto already-archived or rejected issues.
EFFORTS = {'low', 'medium', 'high'}

START, END = '<!-- issues:index:start -->', '<!-- issues:index:end -->'
NAME_RE = re.compile(r'^DELVE-(\d{4})-[a-z0-9-]+\.md$')

# An issue's assets live in an `assets/` directory beside it (issues/assets, issues/archive/assets,
# issues/rejected/assets), named like the issue itself so they sort and grep next to it rather than
# needing a per-issue subdirectory. Referenced from the body as a plain relative Markdown link or
# image: `assets/DELVE-0034-torn-border.png`.
ASSET_DIR_NAME = 'assets'
ASSET_NAME_RE = re.compile(r'^DELVE-\d{4}-[a-z0-9-]+\.[a-z0-9]+$')
ASSET_REF_RE = re.compile(r'\]\(assets/([^)\s]+)\)')
ASSET_MAX_WIDTH = 800


def image_width(path):
    """The pixel width of a PNG or JPEG from its own header, or None if not determinable.

    Stdlib only, no Pillow: a PNG's first chunk after the 8-byte signature is always `IHDR`,
    whose first 8 bytes are big-endian width then height. A JPEG's `SOFn` marker (0xFFC0-0xFFC3,
    excluding the multi-scan 0xFFC4/0xFFC8/0xFFCC) is followed by a 2-byte length, 1-byte
    precision, then big-endian height then width.
    """
    data = path.read_bytes()
    if data[:8] == b'\x89PNG\r\n\x1a\n' and data[12:16] == b'IHDR':
        return int.from_bytes(data[16:20], 'big')
    if data[:2] == b'\xff\xd8':
        i = 2
        while i + 4 <= len(data):
            if data[i] != 0xFF:
                break
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3):
                return int.from_bytes(data[i + 7:i + 9], 'big')
            if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seg_len = int.from_bytes(data[i + 2:i + 4], 'big')
            i += 2 + seg_len
        return None
    return None


# ---------------------------------------------------------------------------- parsing
def parse_front_matter(text):
    """Return the metadata dict from a leading `---` block. Values are str or list[str].

    Deliberately tiny: `key: scalar`, `key: [a, b]`, and `key:` (empty). Good enough for the
    fixed requirement shape, and it gives clearer errors than a general YAML loader would.
    """
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        return None
    meta = {}
    for line in m.group(1).splitlines():
        if not line.strip() or line[0].isspace() or ':' not in line:
            continue
        key, _, raw = line.partition(':')
        key, raw = key.strip(), raw.strip()
        if raw.startswith('[') and raw.endswith(']'):
            inner = raw[1:-1].strip()
            meta[key] = [p.strip() for p in inner.split(',')] if inner else []
        else:
            meta[key] = raw.strip('"').strip("'")
    return meta


def load():
    """All issue files as (path, meta), keyed nowhere; caller sorts. Skips README/TEMPLATE."""
    out = []
    for path in sorted(ISSUES_DIR.rglob('DELVE-*.md')):
        meta = parse_front_matter(path.read_text())
        out.append((path, meta))
    return out


def rel_link(path):
    """Path relative to issues/README.md, forward-slashed for Markdown."""
    return path.relative_to(ISSUES_DIR).as_posix()


def next_id(records):
    """The next free issue id string (e.g. 'DELVE-0016') from the highest filename number."""
    nums = [int(NAME_RE.match(p.name).group(1)) for p, _ in records if NAME_RE.match(p.name)]
    return f'DELVE-{(max(nums) + 1) if nums else 1:04d}'


# ---------------------------------------------------------------------------- index render
def _mermaid_node(req_id, title):
    """A flowchart node: safe id (hyphens break Mermaid) and a quoted label with id + title."""
    safe_id = req_id.replace('-', '_')
    label = f'{req_id}<br/>{title}'.replace('"', '#quot;')
    return f'{safe_id}["{label}"]'


def render_epics_graph(epics, children, by_id):
    """One horizontal Mermaid flowchart per epic, showing that epic and its children."""
    diagrams = []

    def mid(req_id):
        return req_id.replace('-', '_')

    for _path, meta in sorted(epics, key=lambda pm: pm[1]['id']):
        eid = meta['id']
        kids = sorted(children.get(eid, []))
        out = ['```mermaid', 'flowchart LR', f'    {_mermaid_node(eid, meta["title"])}']
        for kid in kids:
            title = by_id[kid]['title'] if kid in by_id else kid
            out.append(f'    {_mermaid_node(kid, title)}')
            out.append(f'    {mid(eid)} --> {mid(kid)}')
        out.append('```')
        diagrams.append('\n'.join(out))
    return '\n\n'.join(diagrams)


def render_index(records):
    """The Markdown that lives between the START/END markers, from sorted (path, meta)."""
    rows = ['| ID | Title | Type | Effort | Status | Version |',
            '|----|-------|------|--------|--------|---------|']
    by_id = {}
    for path, meta in records:
        by_id[meta['id']] = meta
        title = meta['title'].replace('|', r'\|')
        # type/effort are optional (the seed set predates both); show '-' when absent.
        tier = meta.get('type') or '-'
        effort = meta.get('effort') or '-'
        # version_span (e.g. 1.0.1-1.3.4) wins for an arc that spanned releases; else version.
        shown = meta.get('version_span') or meta.get('version') or '-'
        rows.append(f"| [{meta['id']}]({rel_link(path)}) | {title} | {tier} | {effort} | "
                    f"{meta['status']} | {shown} |")
    lines = ['\n'.join(rows)]

    # An epic rolls up its children; the child points up via its `epic:` field, so the whole
    # membership is derivable here and never hand-maintained. This is what makes "all issues
    # of an epic" a query rather than a grep through prose.
    epics = [(p, m) for p, m in records if m.get('type') == 'epic']
    if epics:
        children = {}
        for _p, m in records:
            parent = m.get('epic')
            if parent:
                children.setdefault(parent, []).append(m['id'])
        sec = ['### Epics', '', '| Epic | Title | Children |', '|------|-------|----------|']
        for path, meta in sorted(epics, key=lambda pm: pm[1]['id']):
            kids = ', '.join(sorted(children.get(meta['id'], []))) or '-'
            sec.append(f"| [{meta['id']}]({rel_link(path)}) | "
                       f"{meta['title'].replace('|', chr(92) + '|')} | {kids} |")
        sec.extend(['', render_epics_graph(epics, children, by_id)])
        lines.append('\n'.join(sec))

    rejected = [(p, m) for p, m in records if m['status'] == 'rejected']
    if rejected:
        rej = ['### Rejected', '', '| ID | Title | Reason |', '|----|-------|--------|']
        for path, meta in rejected:
            reason = (meta.get('reason') or '').replace('|', r'\|') or '-'
            rej.append(f"| [{meta['id']}]({rel_link(path)}) | "
                       f"{meta['title'].replace('|', chr(92) + '|')} | {reason} |")
        lines.append('\n'.join(rej))

    lines.append(f'Next free id: **{next_id(records)}**.')
    return '\n\n'.join(lines)


def splice_index(readme_text, block):
    """Replace the content between the markers with `block`."""
    pattern = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.S)
    return pattern.sub(f'{START}\n{block}\n{END}', readme_text, count=1)


# ---------------------------------------------------------------------------- checks
def git_known_commits(shas):
    """Subset of `shas` that git does not recognise; empty when not in a work tree."""
    try:
        inside = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], cwd=ROOT,
                                 capture_output=True, text=True)
        if inside.returncode != 0 or inside.stdout.strip() != 'true':
            return set()
    except FileNotFoundError:
        return set()
    missing = set()
    for sha in shas:
        if sha == PRE_RESET_SENTINEL:
            continue
        r = subprocess.run(['git', 'cat-file', '-e', sha], cwd=ROOT, capture_output=True)
        if r.returncode != 0:
            missing.add(sha)
    return missing


def lint(records):
    """Return a list of human-readable problem strings (empty means clean)."""
    problems = []
    seen_ids = {}
    all_commits = set()
    by_id = {}          # id -> meta, for cross-references (the epic link)
    epic_refs = []      # (where, own_id, own_type, epic_target)
    referenced_assets = {}  # assets dir path -> set of filenames referenced from an issue there

    for path, meta in records:
        where = path.relative_to(ROOT)
        name_m = NAME_RE.match(path.name)
        if not name_m:
            problems.append(f'{where}: filename is not DELVE-NNNN-slug.md')
            continue
        if meta is None:
            problems.append(f'{where}: no front-matter block')
            continue

        missing = [k for k in REQUIRED_KEYS if k not in meta]
        if missing:
            problems.append(f'{where}: missing front-matter keys {missing}')
            continue

        if meta['id'] != f'DELVE-{name_m.group(1)}':
            problems.append(f'{where}: id {meta["id"]} does not match filename')
        seen_ids.setdefault(meta['id'], []).append(str(where))
        by_id[meta['id']] = meta

        # type/epic are optional (the archived seed set predates the tier scheme), but when set
        # they must be sound: a known tier, and an epic link to a real requirement that is itself
        # an epic. This keeps the generated Epics rollup trustworthy.
        tier = meta.get('type')
        if tier and tier not in TYPES:
            problems.append(f'{where}: unknown type {tier!r} ({"|".join(sorted(TYPES))})')
        if meta.get('epic'):
            epic_refs.append((where, meta['id'], tier, meta['epic']))

        # effort is optional too (same backfill reason), but while an issue is proposed/in-progress
        # it must be sized, and any set value must be a known level.
        effort = meta.get('effort')
        if effort and effort not in EFFORTS:
            problems.append(f'{where}: unknown effort {effort!r} ({"|".join(sorted(EFFORTS))})')

        status = meta['status']
        if status in ('proposed', 'in-progress') and not effort:
            problems.append(f'{where}: status {status} must set effort '
                             f'({"|".join(sorted(EFFORTS))})')

        # Peer-review acceptance gate: required only at the proposed -> in-progress transition
        # itself, same backfill exemption as effort (an already-shipped issue may predate the
        # gate; a newly authored one keeps accepted_by once set, so it still shows on archive).
        accepted_by = meta.get('accepted_by')
        accepted_at = meta.get('accepted_at')
        if status == 'in-progress' and not accepted_by:
            problems.append(f'{where}: status {status} must set accepted_by '
                             f'(peer-review acceptance gate)')
        if accepted_by and not accepted_at:
            problems.append(f'{where}: accepted_by is set without accepted_at')
        if accepted_at and not accepted_by:
            problems.append(f'{where}: accepted_at is set without accepted_by')
        if status not in STATUSES:
            problems.append(f'{where}: unknown status {status!r}')
        else:
            top = path.relative_to(ISSUES_DIR).parts[0]
            in_archive, in_rejected = top == 'archive', top == 'rejected'
            in_root = path.parent == ISSUES_DIR
            if status in SHIPPED and not in_archive:
                problems.append(f'{where}: status {status} must live in archive/')
            if status == 'rejected' and not in_rejected:
                problems.append(f'{where}: status rejected must live in rejected/')
            if status in ('proposed', 'in-progress') and not in_root:
                problems.append(f'{where}: status {status} must live in the issues/ root')

        commits = meta['commits']
        if status in SHIPPED and not commits:
            problems.append(f'{where}: status {status} must list at least one commit')
        if status in ('proposed', 'in-progress', 'rejected') and commits:
            problems.append(f'{where}: status {status} must not list commits')
        all_commits.update(commits)

        # An asset lives beside its issue and is named after it, so it moves with the file on
        # archive/reject and never needs a per-issue subdirectory. Track what's referenced here;
        # the orphan half of the check runs once, after every issue has been seen.
        assets_dir = path.parent / ASSET_DIR_NAME
        for ref in ASSET_REF_RE.findall(path.read_text()):
            referenced_assets.setdefault(assets_dir, set()).add(ref)
            if not ref.startswith(f"{meta['id']}-"):
                problems.append(f"{where}: asset reference {ref!r} does not start with its "
                                 f"own id {meta['id']}-")
            if not (assets_dir / ref).is_file():
                problems.append(f'{where}: referenced asset {ASSET_DIR_NAME}/{ref} does not exist')

    for assets_dir in (ISSUES_DIR / ASSET_DIR_NAME, ISSUES_DIR / 'archive' / ASSET_DIR_NAME,
                       ISSUES_DIR / 'rejected' / ASSET_DIR_NAME):
        if not assets_dir.is_dir():
            continue
        used = referenced_assets.get(assets_dir, set())
        for asset in sorted(assets_dir.iterdir()):
            if not asset.is_file():
                continue
            where = asset.relative_to(ROOT)
            if not ASSET_NAME_RE.match(asset.name):
                problems.append(f'{where}: asset filename does not match DELVE-NNNN-slug.ext')
            if asset.name not in used:
                problems.append(f'{where}: orphaned asset, not referenced by any issue in '
                                 f'{assets_dir.relative_to(ROOT)}')
            width = image_width(asset)
            if width is not None and width > ASSET_MAX_WIDTH:
                problems.append(f'{where}: {width}px wide, over the {ASSET_MAX_WIDTH}px cap '
                                 f'(resize it, e.g. sips --resampleWidth {ASSET_MAX_WIDTH})')

    for where, own_id, own_type, target in epic_refs:
        if own_type == 'epic':
            problems.append(f'{where}: an epic must not itself set epic: {target}')
        if target == own_id:
            problems.append(f'{where}: epic: points at itself')
        elif target not in by_id:
            problems.append(f'{where}: epic: {target} is not a known requirement id')
        elif by_id[target].get('type') != 'epic':
            problems.append(f'{where}: epic: {target} is not type: epic')

    for req_id, paths in sorted(seen_ids.items()):
        if len(paths) > 1:
            problems.append(f'duplicate id {req_id} in {paths}')

    nums = sorted(int(i.split('-')[1]) for i in seen_ids)
    if nums and nums != list(range(1, len(nums) + 1)):
        problems.append(f'ids are not contiguous from DELVE-0001: {nums}')

    for sha in sorted(git_known_commits(all_commits)):
        problems.append(f'commit {sha} is not known to git')

    for path in sorted(ISSUES_DIR.rglob('*.md')):
        if '—' in path.read_text():
            problems.append(f'{path.relative_to(ROOT)}: contains an em-dash (repo-wide rule)')

    return problems


# ---------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--check', action='store_true',
                    help='lint and assert the index is current; write nothing')
    args = ap.parse_args(argv)

    records = sorted(load(), key=lambda pm: pm[0].name)
    problems = lint(records)

    readme = README.read_text()
    if START not in readme or END not in readme:
        problems.append(f'{README.relative_to(ROOT)}: missing the {START} / {END} markers')
        rebuilt = readme
    else:
        rebuilt = splice_index(readme, render_index(records))

    if args.check:
        if rebuilt != readme:
            problems.append(f'{README.relative_to(ROOT)}: index is stale; run tools/issues.py')
        if problems:
            print(f'issues: {len(problems)} problem(s):', file=sys.stderr)
            for p in problems:
                print(f'  - {p}', file=sys.stderr)
            return 1
        print(f'ok: {len(records)} issues, ids contiguous, index current; '
              f'next free id: {next_id(records)}')
        return 0

    # write mode
    if problems:
        print('issues: refusing to write, fix these first:', file=sys.stderr)
        for p in problems:
            print(f'  - {p}', file=sys.stderr)
        return 1
    if rebuilt != readme:
        README.write_text(rebuilt)
        print(f'updated {README.relative_to(ROOT)} ({len(records)} issues)')
    else:
        print(f'index already current ({len(records)} issues)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
