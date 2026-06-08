from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .checker import ReadinessReport, check_release_readiness


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="release-readiness-check",
        description="Check whether an open-source repository looks ready for release.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository path to check")
    parser.add_argument("--min-score", type=int, default=70, help="Minimum passing score")
    parser.add_argument("--format", choices=("text", "json", "markdown"), default="text", help="Output format")
    args = parser.parse_args(argv)

    try:
        report = check_release_readiness(Path(args.path))
    except (FileNotFoundError, NotADirectoryError) as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.format == "json":
        print(_json(report))
    elif args.format == "markdown":
        print(_markdown(report, args.min_score))
    else:
        print(_text(report, args.min_score))

    return 0 if report.score >= args.min_score else 1


def _text(report: ReadinessReport, min_score: int) -> str:
    lines = [
        f"Release Readiness Check: {report.root}",
        "",
        f"Score: {report.score}% ({report.passed_points}/{report.total_points})",
        f"Required: {min_score}%",
        "",
    ]

    for check in report.checks:
        status = "PASS" if check.passed else "WARN"
        lines.append(f"{status:<5} {check.name:<18} {check.detail}")

    return "\n".join(lines)


def _json(report: ReadinessReport) -> str:
    payload = {
        "root": str(report.root),
        "score": report.score,
        "points": {
            "passed": report.passed_points,
            "total": report.total_points,
        },
        "checks": [
            {
                "name": check.name,
                "passed": check.passed,
                "detail": check.detail,
                "weight": check.weight,
            }
            for check in report.checks
        ],
    }
    return json.dumps(payload, indent=2)


def _markdown(report: ReadinessReport, min_score: int) -> str:
    lines = [
        "# Release Readiness Check",
        "",
        f"Repository: `{report.root}`",
        "",
        f"Score: **{report.score}% ({report.passed_points}/{report.total_points})**",
        f"Required: **{min_score}%**",
        "",
        "| Status | Check | Detail |",
        "| --- | --- | --- |",
    ]

    for check in report.checks:
        status = "PASS" if check.passed else "WARN"
        lines.append(f"| {status} | {check.name} | {check.detail} |")

    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
