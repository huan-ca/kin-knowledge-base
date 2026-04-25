import json
import subprocess
import sys
from pathlib import Path

INIT_SCRIPT = Path("skills/llm-knowledge-base/scripts/init_repo.py").resolve()
MANIFEST_SCRIPT = Path("skills/llm-knowledge-base/scripts/update_manifest.py").resolve()


def test_update_manifest_marks_new_changed_and_removed_files(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"
    assert MANIFEST_SCRIPT.exists(), f"missing script: {MANIFEST_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()

    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    first_file = repo / "raw" / "one.txt"
    second_file = repo / "raw" / "two.txt"
    first_file.write_text("alpha", encoding="utf-8")
    second_file.write_text("beta", encoding="utf-8")

    subprocess.run([sys.executable, str(MANIFEST_SCRIPT), str(repo), "--batch-id", "batch-001"], check=True)

    first_file.write_text("alpha-updated", encoding="utf-8")
    second_file.unlink()
    third_file = repo / "raw" / "three.txt"
    third_file.write_text("gamma", encoding="utf-8")

    subprocess.run([sys.executable, str(MANIFEST_SCRIPT), str(repo), "--batch-id", "batch-002"], check=True)

    manifest_path = repo / ".kb-state" / "raw-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    history = json.loads((repo / ".kb-state" / "ingestion-history.json").read_text(encoding="utf-8"))

    files = manifest["files"]
    assert files["raw/one.txt"]["status"] == "changed"
    assert files["raw/three.txt"]["status"] == "new"
    assert files["raw/two.txt"]["status"] == "removed"
    assert files["raw/two.txt"]["present"] is False
    assert manifest["last_scan_batch_id"] == "batch-002"
    assert history["batches"][-1]["batch_id"] == "batch-002"
    assert history["batches"][-1]["summary"] == {"changed": 1, "new": 1, "removed": 1, "unchanged": 0}
