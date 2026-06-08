from pathlib import Path

from release_readiness_check.cli import main


def test_cli_outputs_score(tmp_path: Path, capsys) -> None:
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")

    exit_code = main([str(tmp_path), "--min-score", "0"])

    assert exit_code == 0
    assert "Score:" in capsys.readouterr().out


def test_cli_can_output_markdown(tmp_path: Path, capsys) -> None:
    (tmp_path / "README.md").write_text("# Project\n", encoding="utf-8")

    exit_code = main([str(tmp_path), "--min-score", "0", "--format", "markdown"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "# Release Readiness Check" in output
    assert "| Status | Check | Detail |" in output
    assert "| PASS | README | README.md found |" in output
