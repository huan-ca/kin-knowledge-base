import subprocess
import sys
from pathlib import Path

SCRIPT = Path("skills/llm-knowledge-base/scripts/init_repo.py").resolve()


def test_init_repo_bootstraps_expected_layout(tmp_path):
    assert SCRIPT.exists(), f"missing script: {SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()

    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    for relative_path in (
        "knowledge-base.yaml",
        "raw",
        "kb",
        "generated",
        "published",
        ".kb-state",
        ".kb-state/raw-manifest.json",
        ".kb-state/ingestion-plan.json",
        ".kb-state/ingestion-history.json",
        ".kb-state/proposed-types.json",
    ):
        assert (repo / relative_path).exists(), relative_path

    config_text = (repo / "knowledge-base.yaml").read_text(encoding="utf-8")
    assert "canonical_domain_types:" in config_text
    assert "confidence_rubric:" in config_text

    manifest_text = (repo / ".kb-state" / "raw-manifest.json").read_text(encoding="utf-8")
    assert '"files": {}' in manifest_text
