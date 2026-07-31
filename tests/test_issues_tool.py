"""tools/issues.py's peer-review acceptance gate (DELVE-0045): lint() flags a missing
accepted_by on an in-progress issue, and an accepted_by/accepted_at pair set without its
partner, but never on a still-proposed issue.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import issues as issues_tool  # noqa: E402


def _issue_text(status, accepted_by=None, accepted_at=None):
    lines = [
        '---',
        'id: DELVE-0001',
        'title: Test issue',
        f'status: {status}',
        'area: []',
        'effort: low',
        'version:',
        'created: 2026-01-01',
        'updated: 2026-01-01',
    ]
    if accepted_by is not None:
        lines.append(f'accepted_by: {accepted_by}')
    if accepted_at is not None:
        lines.append(f'accepted_at: {accepted_at}')
    lines += ['commits: []', 'related: []', 'supersedes: []', 'docs: []', '---', '', '# Test', '']
    return '\n'.join(lines)


def _lint_one(tmp_path, monkeypatch, status, accepted_by=None, accepted_at=None):
    monkeypatch.setattr(issues_tool, 'ISSUES_DIR', tmp_path)
    monkeypatch.setattr(issues_tool, 'ROOT', tmp_path)
    path = tmp_path / 'DELVE-0001-test.md'
    path.write_text(_issue_text(status, accepted_by, accepted_at))
    meta = issues_tool.parse_front_matter(path.read_text())
    return issues_tool.lint([(path, meta)])


def test_in_progress_without_accepted_by_is_rejected(tmp_path, monkeypatch):
    problems = _lint_one(tmp_path, monkeypatch, 'in-progress')
    assert any('accepted_by' in p for p in problems)


def test_accepted_by_without_accepted_at_is_rejected(tmp_path, monkeypatch):
    problems = _lint_one(tmp_path, monkeypatch, 'in-progress', accepted_by='Alice')
    assert any('accepted_at' in p for p in problems)


def test_proposed_does_not_require_acceptance(tmp_path, monkeypatch):
    problems = _lint_one(tmp_path, monkeypatch, 'proposed')
    assert not any('accepted_by' in p or 'accepted_at' in p for p in problems)


def test_in_progress_with_both_fields_passes_the_gate(tmp_path, monkeypatch):
    problems = _lint_one(tmp_path, monkeypatch, 'in-progress',
                          accepted_by='Alice', accepted_at='2026-01-02')
    assert not any('accepted_by' in p or 'accepted_at' in p for p in problems)
