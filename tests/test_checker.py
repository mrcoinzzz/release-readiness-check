from pathlib import Path

from release_readiness_check.checker import check_release_readiness


def test_check_release_readiness_finds_core_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")
    (tmp_path / "LICENSE").write_text("MIT\n", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nversion = \"1.0.0\"\n", encoding="utf-8")

    report = check_release_readiness(tmp_path)

    passed = {check.name for check in report.checks if check.passed}
    assert "README" in passed
    assert "License" in passed
    assert "Changelog" in passed
    assert "Package metadata" in passed
    assert "Version metadata" in passed


def test_missing_path_raises_file_not_found() -> None:
    missing = Path("/definitely/not/a/release/readiness/path")

    try:
        check_release_readiness(missing)
    except FileNotFoundError as error:
        assert "Path does not exist" in str(error)
    else:
        raise AssertionError("Expected FileNotFoundError")
