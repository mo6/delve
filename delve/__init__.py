"""Delve: a NetHack-style training application.

Learners descend a dungeon; keepers teach a topic and examine them on it; passing
makes a door appear. See docs/PLAN.md for the design and CLAUDE.md for the rules that
are expensive to get wrong.
"""

# 1.0.0 is the release: M1-M8 done, the pilot plays end to end in English and Dutch. The pre-1.0
# scheme was 0.<milestone>.<patch> (it reached 0.8.4); from 1.0.0 on it is ordinary semver,
# MAJOR.MINOR.PATCH. M7 content-tuning from real play evidence continues as post-1.0 patch
# releases. Keep pyproject.toml's version in step (nothing syncs the two files).
__version__ = "1.36.1"
