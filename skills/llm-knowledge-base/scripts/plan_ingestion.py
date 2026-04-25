from __future__ import annotations

import argparse
from pathlib import Path

from common import read_json, write_json


def build_plan(repo_root: Path) -> dict:
    manifest = read_json(repo_root / ".kb-state" / "raw-manifest.json", {"files": {}})
    files = manifest.get("files", {})

    to_ingest = []
    removed = []
    unchanged = []

    for relative_path in sorted(files):
        entry = files[relative_path]
        if not entry.get("present", True):
            removed.append(entry)
            continue

        if entry.get("last_ingested_hash") != entry.get("sha256") or not entry.get("source_page_id"):
            to_ingest.append(entry)
        else:
            unchanged.append(entry)

    return {
        "to_ingest": to_ingest,
        "removed": removed,
        "unchanged": unchanged,
        "summary": {
            "removed": len(removed),
            "to_ingest": len(to_ingest),
            "unchanged": len(unchanged),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan which raw files need knowledge-base ingestion.")
    parser.add_argument("repo_root", help="Path to the repo root.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    plan = build_plan(repo_root)
    write_json(repo_root / ".kb-state" / "ingestion-plan.json", plan)


if __name__ == "__main__":
    main()
