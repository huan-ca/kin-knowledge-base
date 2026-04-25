import json
import subprocess
import sys
from pathlib import Path

INIT_SCRIPT = Path("skills/llm-knowledge-base/scripts/init_repo.py").resolve()
PLAN_SCRIPT = Path("skills/llm-knowledge-base/scripts/plan_ingestion.py").resolve()


def test_plan_ingestion_selects_files_needing_ingestion(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"
    assert PLAN_SCRIPT.exists(), f"missing script: {PLAN_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    manifest = {
        "format_version": 1,
        "last_scan_batch_id": "batch-009",
        "files": {
            "raw/new.txt": {
                "relative_path": "raw/new.txt",
                "sha256": "hash-new",
                "status": "new",
                "present": True,
                "last_ingested_hash": None,
                "source_page_id": None,
            },
            "raw/changed.txt": {
                "relative_path": "raw/changed.txt",
                "sha256": "hash-changed-now",
                "status": "changed",
                "present": True,
                "last_ingested_hash": "hash-changed-before",
                "source_page_id": "source-changed",
            },
            "raw/steady.txt": {
                "relative_path": "raw/steady.txt",
                "sha256": "hash-same",
                "status": "unchanged",
                "present": True,
                "last_ingested_hash": "hash-same",
                "source_page_id": "source-steady",
            },
            "raw/removed.txt": {
                "relative_path": "raw/removed.txt",
                "sha256": "hash-removed",
                "status": "removed",
                "present": False,
                "last_ingested_hash": "hash-removed",
                "source_page_id": "source-removed",
            },
        },
    }
    (repo / ".kb-state" / "raw-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    subprocess.run([sys.executable, str(PLAN_SCRIPT), str(repo)], check=True)

    plan = json.loads((repo / ".kb-state" / "ingestion-plan.json").read_text(encoding="utf-8"))
    assert [item["relative_path"] for item in plan["to_ingest"]] == ["raw/changed.txt", "raw/new.txt"]
    assert [item["relative_path"] for item in plan["removed"]] == ["raw/removed.txt"]
    assert [item["relative_path"] for item in plan["unchanged"]] == ["raw/steady.txt"]
    assert plan["summary"] == {"removed": 1, "to_ingest": 2, "unchanged": 1}


def test_plan_ingestion_selects_restored_file_with_cleared_ingest_markers(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    manifest = {
        "format_version": 1,
        "last_scan_batch_id": "batch-010",
        "files": {
            "raw/restored.txt": {
                "relative_path": "raw/restored.txt",
                "sha256": "hash-restored",
                "status": "changed",
                "present": True,
                "last_ingested_hash": None,
                "source_page_id": None,
            }
        },
    }
    (repo / ".kb-state" / "raw-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    subprocess.run([sys.executable, str(PLAN_SCRIPT), str(repo)], check=True)

    plan = json.loads((repo / ".kb-state" / "ingestion-plan.json").read_text(encoding="utf-8"))
    assert [item["relative_path"] for item in plan["to_ingest"]] == ["raw/restored.txt"]
    assert plan["removed"] == []
    assert plan["unchanged"] == []
    assert plan["summary"] == {"removed": 0, "to_ingest": 1, "unchanged": 0}
