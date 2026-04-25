from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from common import read_json, sha256_file, write_json


def build_batch_id(explicit_batch_id: str | None) -> str:
    if explicit_batch_id:
        return explicit_batch_id
    return datetime.now(timezone.utc).strftime("batch-%Y%m%dT%H%M%SZ")


def scan_repo(repo_root: Path, batch_id: str) -> dict:
    manifest_path = repo_root / ".kb-state" / "raw-manifest.json"
    previous = read_json(manifest_path, {"format_version": 1, "files": {}, "last_scan_batch_id": None})
    previous_files = previous.get("files", {})

    current_files: dict[str, dict] = {}
    seen_paths: set[str] = set()

    for path in sorted((repo_root / "raw").rglob("*")):
        if not path.is_file():
            continue

        relative_path = path.relative_to(repo_root).as_posix()
        sha256 = sha256_file(path)
        previous_entry = previous_files.get(relative_path, {})
        previous_hash = previous_entry.get("sha256")

        if previous_hash is None:
            status = "new"
        elif previous_hash == sha256:
            status = "unchanged"
        else:
            status = "changed"

        current_files[relative_path] = {
            "relative_path": relative_path,
            "sha256": sha256,
            "size": path.stat().st_size,
            "modified_timestamp": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
            "import_batch_id": batch_id,
            "present": True,
            "status": status,
            "last_ingested_hash": previous_entry.get("last_ingested_hash"),
            "source_page_id": previous_entry.get("source_page_id"),
        }
        seen_paths.add(relative_path)

    for relative_path, previous_entry in previous_files.items():
        if relative_path in seen_paths:
            continue
        current_files[relative_path] = {
            **previous_entry,
            "relative_path": relative_path,
            "present": False,
            "status": "removed",
            "import_batch_id": batch_id,
        }

    return {
        "format_version": 1,
        "last_scan_batch_id": batch_id,
        "files": current_files,
    }


def build_history_entry(manifest: dict, batch_id: str) -> dict:
    summary = {"new": 0, "changed": 0, "removed": 0, "unchanged": 0}
    for entry in manifest["files"].values():
        status = entry["status"]
        if status in summary:
            summary[status] += 1
    return {
        "batch_id": batch_id,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Update the raw-file manifest for a knowledge-base repo.")
    parser.add_argument("repo_root", help="Path to the repo root.")
    parser.add_argument("--batch-id", help="Optional explicit batch identifier.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    batch_id = build_batch_id(args.batch_id)
    manifest = scan_repo(repo_root, batch_id)
    write_json(repo_root / ".kb-state" / "raw-manifest.json", manifest)

    history_path = repo_root / ".kb-state" / "ingestion-history.json"
    history = read_json(history_path, {"batches": []})
    history["batches"].append(build_history_entry(manifest, batch_id))
    write_json(history_path, history)


if __name__ == "__main__":
    main()
