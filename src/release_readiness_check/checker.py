from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str
    weight: int = 10


@dataclass(frozen=True)
class ReadinessReport:
    root: Path
    checks: tuple[CheckResult, ...]

    @property
    def passed_points(self) -> int:
        return sum(check.weight for check in self.checks if check.passed)

    @property
    def total_points(self) -> int:
        return sum(check.weight for check in self.checks)

    @property
    def score(self) -> int:
        if self.total_points == 0:
            return 0
        return round((self.passed_points / self.total_points) * 100)


def check_release_readiness(root: str | Path) -> ReadinessReport:
    repo_root = Path(root).expanduser().resolve()
    if not repo_root.exists():
        raise FileNotFoundError(f"Path does not exist: {repo_root}")
    if not repo_root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {repo_root}")

    checks = (
        _exists(repo_root, "README", ("README.md", "README.rst", "README.txt")),
        _exists(repo_root, "License", ("LICENSE", "LICENSE.md", "COPYING")),
        _exists(repo_root, "Changelog", ("CHANGELOG.md", "RELEASE_NOTES.md", "HISTORY.md")),
        _exists(repo_root, "Security policy", ("SECURITY.md", ".github/SECURITY.md")),
        _exists(repo_root, "CI workflow", (".github/workflows",)),
        _exists(repo_root, "Tests", ("tests", "test", "__tests__")),
        _exists(repo_root, "Package metadata", ("pyproject.toml", "package.json", "Cargo.toml", "go.mod")),
        _has_version_metadata(repo_root),
        _git_repository(repo_root),
        _clean_working_tree(repo_root),
    )
    return ReadinessReport(root=repo_root, checks=checks)


def _exists(root: Path, name: str, candidates: Iterable[str]) -> CheckResult:
    for candidate in candidates:
        if (root / candidate).exists():
            return CheckResult(name=name, passed=True, detail=f"{candidate} found")
    return CheckResult(name=name, passed=False, detail=f"Missing one of: {', '.join(candidates)}")


def _has_version_metadata(root: Path) -> CheckResult:
    files = ("pyproject.toml", "package.json", "Cargo.toml")
    for filename in files:
        path = root / filename
        if path.exists() and "version" in path.read_text(encoding="utf-8", errors="ignore"):
            return CheckResult("Version metadata", True, f"version found in {filename}")
    return CheckResult("Version metadata", False, "Add a version field to package metadata")


def _git_repository(root: Path) -> CheckResult:
    if (root / ".git").exists():
        return CheckResult("Git repository", True, ".git found")
    return CheckResult("Git repository", False, "Initialize a git repository before release")


def _clean_working_tree(root: Path) -> CheckResult:
    if not (root / ".git").exists():
        return CheckResult("Clean working tree", False, "Not a git repository")

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        return CheckResult("Clean working tree", False, f"Could not inspect git status: {error}")

    if result.stdout.strip():
        return CheckResult("Clean working tree", False, "Uncommitted changes found")
    return CheckResult("Clean working tree", True, "No uncommitted changes")
