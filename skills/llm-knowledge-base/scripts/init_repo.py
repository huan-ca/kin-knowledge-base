from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_dir, templates_root, write_json, write_text


README_TEXT = {
    "kb/README.md": "# Knowledge Base\n\nThis directory is Codex-managed derived knowledge rebuilt from `raw/` plus `knowledge-base.yaml`.\n",
    "generated/README.md": "# Generated Outputs\n\nThis directory contains reproducible generated artifacts derived from `kb/`.\n\nJob-scoped outputs should live under `generated/<job-name>/`.\nRepo-wide reports remain under `generated/reports/`.\n",
    "published/README.md": "# Published Outputs\n\nMove human-maintained outputs here once they should no longer be overwritten automatically.\n",
}


STATE_FILES = {
    ".kb-state/raw-manifest.json": {"format_version": 1, "files": {}, "last_scan_batch_id": None},
    ".kb-state/ingestion-plan.json": {"to_ingest": [], "removed": [], "unchanged": [], "summary": {}},
    ".kb-state/ingestion-history.json": {"batches": []},
    ".kb-state/proposed-types.json": {"proposed_types": []},
}


def build_repo(repo_root: Path, force: bool = False) -> None:
    for relative_dir in ("raw", "kb", "generated", "published", ".kb-state"):
        ensure_dir(repo_root / relative_dir)

    config_template = (templates_root() / "knowledge-base.yaml").read_text(encoding="utf-8")
    write_text(repo_root / "knowledge-base.yaml", config_template, overwrite=force)

    for relative_path, content in README_TEXT.items():
        write_text(repo_root / relative_path, content, overwrite=force)

    for relative_path, payload in STATE_FILES.items():
        path = repo_root / relative_path
        if force or not path.exists():
            write_json(path, payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a repo for the llm-knowledge-base skill.")
    parser.add_argument("repo_root", help="Path to the repo root that should receive the knowledge-base layout.")
    parser.add_argument("--force", action="store_true", help="Overwrite starter files when they already exist.")
    args = parser.parse_args()

    build_repo(Path(args.repo_root).resolve(), force=args.force)


if __name__ == "__main__":
    main()
