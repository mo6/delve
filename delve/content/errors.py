"""Author-facing errors. Everything a pack author sees points at `file:line`, because the
audience for these is someone editing Markdown, not reading a Python traceback (AUTHORING.md
section 12, PLAN.md section 4).

Two shapes. `PackError` is raised when a file is malformed enough that no object can be built
from it (a missing frontmatter fence, a question with no heading). An `Issue` is a semantic
finding collected during validation, and unlike an exception a whole pack's worth of them is
gathered and reported together, so one run of `delve validate` shows every problem at once.
"""

from dataclasses import dataclass


def _where(path: str, line: int | None) -> str:
    return f"{path}:{line}" if line else path


class PackError(Exception):
    """A file could not be parsed at all. Carries the location so the CLI can print file:line."""

    def __init__(self, path: str, line: int | None, message: str):
        self.path = path
        self.line = line
        self.message = message
        super().__init__(f"{_where(path, line)}: {message}")


@dataclass(frozen=True)
class Issue:
    """One validation finding. `error` blocks the pack; `warning` is advisory (a chapter of
    seven rooms is legal but a smell). Sorted and printed by the CLI as `file:line: message`."""

    path: str
    line: int | None
    message: str
    level: str = "error"      # 'error' | 'warning'

    @property
    def is_error(self) -> bool:
        return self.level == "error"

    def __str__(self) -> str:
        return f"{_where(self.path, self.line)}: {self.level}: {self.message}"
