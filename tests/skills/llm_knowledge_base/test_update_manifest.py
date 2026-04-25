import json
import subprocess
import sys
from pathlib import Path

INIT_SCRIPT = Path("skills/llm-knowledge-base/scripts/init_repo.py").resolve()
MANIFEST_SCRIPT = Path("skills/llm-knowledge-base/scripts/update_manifest.py").resolve()


def should_task4_ingest(entry: dict) -> bool:
    return entry["present"] and (
        entry["status"] != "unchanged"
        or entry.get("last_ingested_hash") != entry["sha256"]
        or entry.get("source_page_id") is None
    )


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


def test_update_manifest_does_not_repeat_prior_removal_in_later_no_op_scan(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()

    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    first_file = repo / "raw" / "one.txt"
    second_file = repo / "raw" / "two.txt"
    first_file.write_text("alpha", encoding="utf-8")
    second_file.write_text("beta", encoding="utf-8")

    subprocess.run([sys.executable, str(MANIFEST_SCRIPT), str(repo), "--batch-id", "batch-001"], check=True)

    second_file.unlink()
    subprocess.run([sys.executable, str(MANIFEST_SCRIPT), str(repo), "--batch-id", "batch-002"], check=True)
    subprocess.run([sys.executable, str(MANIFEST_SCRIPT), str(repo), "--batch-id", "batch-003"], check=True)

    history = json.loads((repo / ".kb-state" / "ingestion-history.json").read_text(encoding="utf-8"))

    assert history["batches"][-2]["summary"] == {"changed": 0, "new": 0, "removed": 1, "unchanged": 1}
    assert history["batches"][-1]["batch_id"] == "batch-003"
    assert history["batches"][-1]["summary"] == {"changed": 0, "new": 0, "removed": 0, "unchanged": 1}


def test_update_manifest_marks_restored_file_with_same_bytes_as_changed(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()

    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    restored_file = repo / "raw" / "one.txt"
    restored_file.write_text("alpha", encoding="utf-8")

    subprocess.run([sys.executable, str(MANIFEST_SCRIPT), str(repo), "--batch-id", "batch-001"], check=True)

    manifest_path = repo / ".kb-state" / "raw-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"]["raw/one.txt"]["last_ingested_hash"] = manifest["files"]["raw/one.txt"]["sha256"]
    manifest["files"]["raw/one.txt"]["source_page_id"] = "page-123"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    restored_file.unlink()
    subprocess.run([sys.executable, str(MANIFEST_SCRIPT), str(repo), "--batch-id", "batch-002"], check=True)

    restored_file.write_text("alpha", encoding="utf-8")
    subprocess.run([sys.executable, str(MANIFEST_SCRIPT), str(repo), "--batch-id", "batch-003"], check=True)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    restored_entry = manifest["files"]["raw/one.txt"]

    assert restored_entry["status"] == "changed"
    assert restored_entry["present"] is True
    assert restored_entry["last_ingested_hash"] is None
    assert restored_entry["source_page_id"] is None
    assert should_task4_ingest(restored_entry) is True
