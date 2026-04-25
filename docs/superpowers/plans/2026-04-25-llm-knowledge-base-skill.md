# LLM Knowledge Base Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable `skills/llm-knowledge-base` skill that bootstraps a repo-local LLM wiki, tracks raw file changes with hashes, and maintains deterministic KB/report state with provenance, confidence, and gap handling.

**Architecture:** Keep the skill self-contained under `skills/llm-knowledge-base/`. Use stdlib-only Python helper scripts for deterministic filesystem and state work, keep workflow rules in `SKILL.md` plus reference docs, and ship reusable repo/config/page templates in `assets/templates/`. Validate behavior with `pytest` against temp repos and with the upstream skill validator.

**Tech Stack:** Python 3, Markdown, YAML, JSON, `pytest` via `uv run --with pytest`, upstream validator via `uv run --with pyyaml`.

---

## File Structure

Create and maintain these files.

- `skills/llm-knowledge-base/SKILL.md`
  Primary operator guide for bootstrap, ingestion, regeneration, generation, and missing-information handling.
- `skills/llm-knowledge-base/agents/openai.yaml`
  UI metadata regenerated from the finished skill.
- `skills/llm-knowledge-base/scripts/common.py`
  Shared helpers for locating the skill root, creating directories, hashing files, reading/writing JSON, parsing simple frontmatter, and iterating KB markdown files.
- `skills/llm-knowledge-base/scripts/init_repo.py`
  Bootstrap a target repo with `knowledge-base.yaml`, `raw/`, `kb/`, `generated/`, `published/`, and `.kb-state/`.
- `skills/llm-knowledge-base/scripts/update_manifest.py`
  Scan `raw/`, compute hashes, and maintain `.kb-state/raw-manifest.json`.
- `skills/llm-knowledge-base/scripts/plan_ingestion.py`
  Compare current hashes against `last_ingested_hash` and produce `.kb-state/ingestion-plan.json`.
- `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
  Read `kb/` markdown pages and rebuild `kb/index.md`, `generated/reports/gap-report.md`, `generated/reports/conflict-report.md`, `generated/reports/improvement-report.md`, and `.kb-state/link-map.json`.
- `skills/llm-knowledge-base/references/repo-contract.md`
  Directory contract and lifecycle rules.
- `skills/llm-knowledge-base/references/page-types.md`
  Universal page types, domain types, and controlled proposed-type rules.
- `skills/llm-knowledge-base/references/provenance-and-confidence.md`
  Source basis, claim labels, confidence rubric, and missing-information policy.
- `skills/llm-knowledge-base/references/output-patterns.md`
  Curriculum, lesson-plan, report, and policy/culture generation patterns.
- `skills/llm-knowledge-base/assets/templates/knowledge-base.yaml`
  Starter root config copied into target repos.
- `skills/llm-knowledge-base/assets/templates/pages/source.md`
  Template for normalized source pages.
- `skills/llm-knowledge-base/assets/templates/pages/knowledge-page.md`
  Template for `concept`, `procedure`, `glossary-term`, and `decision` pages.
- `skills/llm-knowledge-base/assets/templates/pages/open-question.md`
  Template for explicit knowledge gaps.
- `skills/llm-knowledge-base/assets/templates/pages/report.md`
  Template for generated reports.
- `skills/llm-knowledge-base/assets/templates/pages/domain-page.md`
  Template for domain-specific pages such as `position`, `drill`, or `lesson`.
- `tests/skills/llm_knowledge_base/test_init_repo.py`
  Bootstrap tests.
- `tests/skills/llm_knowledge_base/test_update_manifest.py`
  Raw-manifest scanning tests.
- `tests/skills/llm_knowledge_base/test_plan_ingestion.py`
  Ingestion selection tests.
- `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`
  Index and report rebuild tests.
- `tests/skills/llm_knowledge_base/test_skill_docs.py`
  Documentation smoke tests that keep placeholders out of the final skill.

### Task 1: Scaffold the Skill Directory

**Files:**
- Create: `skills/llm-knowledge-base/SKILL.md`
- Create: `skills/llm-knowledge-base/agents/openai.yaml`
- Create: `skills/llm-knowledge-base/scripts/`
- Create: `skills/llm-knowledge-base/references/`
- Create: `skills/llm-knowledge-base/assets/`

- [ ] **Step 1: Create the plan’s output directory**

Run:

```bash
mkdir -p skills tests/skills/llm_knowledge_base
```

Expected: command exits with status `0`.

- [ ] **Step 2: Run the upstream skill scaffold command**

Run:

```bash
python3 /Users/huan/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  llm-knowledge-base \
  --path /Users/huan/dev/kin/skills \
  --resources scripts,references,assets \
  --interface display_name="LLM Knowledge Base" \
  --interface short_description="Build and maintain linked LLM wikis" \
  --interface default_prompt="Use this skill to create or maintain a linked markdown knowledge base with provenance, confidence, and incremental ingestion."
```

Expected: output includes `[OK] Skill 'llm-knowledge-base' initialized successfully`.

- [ ] **Step 3: Verify the scaffolded file set**

Run:

```bash
find skills/llm-knowledge-base -maxdepth 3 -type f | sort
```

Expected output:

```text
skills/llm-knowledge-base/SKILL.md
skills/llm-knowledge-base/agents/openai.yaml
```

- [ ] **Step 4: Commit the scaffold**

Run:

```bash
git add skills/llm-knowledge-base
git commit -m "chore: scaffold llm knowledge base skill"
```

Expected: a commit is created with the scaffolded skill skeleton.

### Task 2: Add Repo Bootstrap Assets and the Bootstrap Script

**Files:**
- Create: `skills/llm-knowledge-base/scripts/common.py`
- Create: `skills/llm-knowledge-base/scripts/init_repo.py`
- Create: `skills/llm-knowledge-base/assets/templates/knowledge-base.yaml`
- Create: `skills/llm-knowledge-base/assets/templates/pages/source.md`
- Create: `skills/llm-knowledge-base/assets/templates/pages/knowledge-page.md`
- Create: `skills/llm-knowledge-base/assets/templates/pages/open-question.md`
- Create: `skills/llm-knowledge-base/assets/templates/pages/report.md`
- Create: `skills/llm-knowledge-base/assets/templates/pages/domain-page.md`
- Create: `tests/skills/llm_knowledge_base/test_init_repo.py`

- [ ] **Step 1: Write the failing bootstrap test**

Create `tests/skills/llm_knowledge_base/test_init_repo.py`:

```python
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
```

- [ ] **Step 2: Run the bootstrap test to verify it fails**

Run:

```bash
uv run --with pytest pytest tests/skills/llm_knowledge_base/test_init_repo.py -q
```

Expected: FAIL with `missing script` because `init_repo.py` does not exist yet.

- [ ] **Step 3: Write the shared helper module**

Create `skills/llm-knowledge-base/scripts/common.py`:

```python
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def templates_root() -> Path:
    return skill_root() / "assets" / "templates"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str, overwrite: bool = False) -> None:
    ensure_dir(path.parent)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value in {"true", "false"}:
        return value == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text

    _, remainder = text.split("---\n", 1)
    header, body = remainder.split("\n---\n", 1)

    metadata: dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in header.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("- ") and current_key:
            metadata.setdefault(current_key, []).append(parse_scalar(line[2:]))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            metadata[key] = parse_scalar(value)
            current_key = None
        else:
            metadata[key] = []
            current_key = key

    return metadata, body


def iter_markdown_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        path
        for path in root.rglob("*.md")
        if path.is_file() and path.name not in {"README.md", "index.md"}
    )
```

- [ ] **Step 4: Write the repo initializer**

Create `skills/llm-knowledge-base/scripts/init_repo.py`:

```python
from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_dir, read_json, templates_root, write_json, write_text


README_TEXT = {
    "kb/README.md": "# Knowledge Base\n\nThis directory is Codex-managed derived knowledge rebuilt from `raw/` plus `knowledge-base.yaml`.\n",
    "generated/README.md": "# Generated Outputs\n\nThis directory contains reproducible generated artifacts derived from `kb/`.\n",
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
        else:
            read_json(path, payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize a repo for the llm-knowledge-base skill.")
    parser.add_argument("repo_root", help="Path to the repo root that should receive the knowledge-base layout.")
    parser.add_argument("--force", action="store_true", help="Overwrite starter files when they already exist.")
    args = parser.parse_args()

    build_repo(Path(args.repo_root).resolve(), force=args.force)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Add the starter templates**

Create `skills/llm-knowledge-base/assets/templates/knowledge-base.yaml`:

```yaml
domain_name: "Example Domain"
canonical_domain_types:
  - lesson
  - curriculum-unit
required_page_metadata:
  - id
  - type
  - title
  - status
  - confidence
confidence_rubric:
  1.0: "Directly supported by multiple source chunks with no conflict."
  0.8: "Directly supported by one clear source chunk."
  0.6: "Reasonable inference from available material."
  0.4: "Weakly supported, incomplete, or partially conflicting."
  0.2: "Open question or unsupported request."
generation_targets:
  - curriculum
  - lesson-plan
  - gap-report
  - improvement-report
proposal_policy:
  auto_allow_proposed_types: false
repo_contract:
  raw_dir: raw
  kb_dir: kb
  generated_dir: generated
  published_dir: published
  state_dir: .kb-state
```

Create `skills/llm-knowledge-base/assets/templates/pages/source.md`:

```md
---
id: source-{{ slug }}
type: source
title: "{{ title }}"
status: active
confidence: 1.0
source_refs: []
related_pages: []
ingestion_batch: {{ batch_id }}
---
# {{ title }}

## Artifact
- Path: `raw/{{ relative_path }}`
- Hash: `{{ sha256 }}`

## Summary
[Summarize only what the artifact supports.]

## Extracted Claims
- [Claim text] (`chunk-001`)

## Open Questions
- [Missing or ambiguous point]
```

Create `skills/llm-knowledge-base/assets/templates/pages/knowledge-page.md`:

```md
---
id: {{ page_id }}
type: concept
title: "{{ title }}"
status: draft
confidence: 0.5
claim_label: fact
source_refs:
- source-{{ source_slug }}#chunk-001
related_pages: []
domain_tags: []
---
# {{ title }}

## Canonical Statement
[State the claim without exceeding the available evidence.]

## Supporting Evidence
- [Quoted or paraphrased support tied to a source chunk]

## Related Pages
- [[related-page]]

## Missing Information
- [What is still unknown]
```

Create `skills/llm-knowledge-base/assets/templates/pages/open-question.md`:

```md
---
id: open-question-{{ slug }}
type: open-question
title: "{{ title }}"
status: unresolved
confidence: 0.2
source_refs: []
related_pages: []
---
# {{ title }}

## Missing Information
- [What information is required]

## Why It Matters
- [What downstream generation is blocked or weakened]

## Candidate Sources
- [Which raw files or future documents might resolve this]
```

Create `skills/llm-knowledge-base/assets/templates/pages/report.md`:

```md
---
id: report-{{ slug }}
type: report
title: "{{ title }}"
status: generated
confidence: 0.7
source_refs: []
related_pages: []
---
# {{ title }}

## Summary
- [Concise generated finding]

## Findings
- [Observation with page links]

## Recommended Improvements
- [Suggested next step]
```

Create `skills/llm-knowledge-base/assets/templates/pages/domain-page.md`:

```md
---
id: {{ page_id }}
type: {{ domain_type }}
title: "{{ title }}"
status: draft
confidence: 0.5
claim_label: fact
source_refs:
- source-{{ source_slug }}#chunk-001
related_pages: []
domain_tags:
- {{ domain_type }}
---
# {{ title }}

## Definition
[Describe the domain-specific item with explicit provenance.]

## Key Details
- [Detail one]
- [Detail two]

## Related Pages
- [[related-page]]

## Gaps
- [What remains unclear]
```

- [ ] **Step 6: Run the bootstrap test to verify it passes**

Run:

```bash
uv run --with pytest pytest tests/skills/llm_knowledge_base/test_init_repo.py -q
```

Expected: PASS with `1 passed`.

- [ ] **Step 7: Commit the bootstrap implementation**

Run:

```bash
git add \
  skills/llm-knowledge-base/scripts/common.py \
  skills/llm-knowledge-base/scripts/init_repo.py \
  skills/llm-knowledge-base/assets/templates \
  tests/skills/llm_knowledge_base/test_init_repo.py
git commit -m "feat: add llm knowledge base repo bootstrap"
```

Expected: a commit is created for the bootstrap workflow.

### Task 3: Add Raw Manifest Scanning

**Files:**
- Create: `skills/llm-knowledge-base/scripts/update_manifest.py`
- Create: `tests/skills/llm_knowledge_base/test_update_manifest.py`

- [ ] **Step 1: Write the failing manifest test**

Create `tests/skills/llm_knowledge_base/test_update_manifest.py`:

```python
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
```

- [ ] **Step 2: Run the manifest test to verify it fails**

Run:

```bash
uv run --with pytest pytest tests/skills/llm_knowledge_base/test_update_manifest.py -q
```

Expected: FAIL with `missing script` because `update_manifest.py` does not exist yet.

- [ ] **Step 3: Write the manifest updater**

Create `skills/llm-knowledge-base/scripts/update_manifest.py`:

```python
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
```

- [ ] **Step 4: Run the manifest test to verify it passes**

Run:

```bash
uv run --with pytest pytest tests/skills/llm_knowledge_base/test_update_manifest.py -q
```

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit the manifest updater**

Run:

```bash
git add \
  skills/llm-knowledge-base/scripts/update_manifest.py \
  tests/skills/llm_knowledge_base/test_update_manifest.py
git commit -m "feat: add raw manifest scanning"
```

Expected: a commit is created for manifest maintenance.

### Task 4: Add Ingestion Planning

**Files:**
- Create: `skills/llm-knowledge-base/scripts/plan_ingestion.py`
- Create: `tests/skills/llm_knowledge_base/test_plan_ingestion.py`

- [ ] **Step 1: Write the failing ingestion-plan test**

Create `tests/skills/llm_knowledge_base/test_plan_ingestion.py`:

```python
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
```

- [ ] **Step 2: Run the ingestion-plan test to verify it fails**

Run:

```bash
uv run --with pytest pytest tests/skills/llm_knowledge_base/test_plan_ingestion.py -q
```

Expected: FAIL with `missing script` because `plan_ingestion.py` does not exist yet.

- [ ] **Step 3: Write the ingestion planner**

Create `skills/llm-knowledge-base/scripts/plan_ingestion.py`:

```python
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
```

- [ ] **Step 4: Run the ingestion-plan test to verify it passes**

Run:

```bash
uv run --with pytest pytest tests/skills/llm_knowledge_base/test_plan_ingestion.py -q
```

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit the ingestion planner**

Run:

```bash
git add \
  skills/llm-knowledge-base/scripts/plan_ingestion.py \
  tests/skills/llm_knowledge_base/test_plan_ingestion.py
git commit -m "feat: add ingestion planning"
```

Expected: a commit is created for ingestion planning.

### Task 5: Rebuild Indexes and Reports from KB Pages

**Files:**
- Create: `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
- Create: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`

- [ ] **Step 1: Write the failing index rebuild test**

Create `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

INIT_SCRIPT = Path("skills/llm-knowledge-base/scripts/init_repo.py").resolve()
REBUILD_SCRIPT = Path("skills/llm-knowledge-base/scripts/rebuild_indexes.py").resolve()


def test_rebuild_indexes_creates_index_gap_report_conflict_report_and_link_map(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"
    assert REBUILD_SCRIPT.exists(), f"missing script: {REBUILD_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    concept_page = repo / "kb" / "concepts" / "closed-guard.md"
    concept_page.parent.mkdir(parents=True, exist_ok=True)
    concept_page.write_text(
        \"\"\"---
id: closed-guard
type: concept
title: Closed Guard
status: active
confidence: 0.9
source_refs:
- source-compendium#chunk-001
related_pages:
- armbar
---
# Closed Guard
\"\"\",
        encoding="utf-8",
    )

    open_question_page = repo / "kb" / "open-questions" / "missing-drill-detail.md"
    open_question_page.parent.mkdir(parents=True, exist_ok=True)
    open_question_page.write_text(
        \"\"\"---
id: missing-drill-detail
type: open-question
title: Missing Drill Detail
status: unresolved
confidence: 0.2
source_refs: []
related_pages: []
---
# Missing Drill Detail
\"\"\",
        encoding="utf-8",
    )

    conflict_page = repo / "kb" / "concepts" / "conflicting-terminology.md"
    conflict_page.write_text(
        \"\"\"---
id: conflicting-terminology
type: concept
title: Conflicting Terminology
status: conflict
confidence: 0.4
source_refs:
- source-overview#chunk-002
related_pages: []
---
# Conflicting Terminology
\"\"\",
        encoding="utf-8",
    )

    subprocess.run([sys.executable, str(REBUILD_SCRIPT), str(repo)], check=True)

    index_text = (repo / "kb" / "index.md").read_text(encoding="utf-8")
    gap_report_text = (repo / "generated" / "reports" / "gap-report.md").read_text(encoding="utf-8")
    conflict_report_text = (repo / "generated" / "reports" / "conflict-report.md").read_text(encoding="utf-8")
    improvement_report_text = (repo / "generated" / "reports" / "improvement-report.md").read_text(encoding="utf-8")
    link_map = json.loads((repo / ".kb-state" / "link-map.json").read_text(encoding="utf-8"))

    assert "Closed Guard" in index_text
    assert "Missing Drill Detail" in gap_report_text
    assert "Conflicting Terminology" in conflict_report_text
    assert "Add or refine source material" in improvement_report_text
    assert link_map["closed-guard"]["related_pages"] == ["armbar"]
```

- [ ] **Step 2: Run the index rebuild test to verify it fails**

Run:

```bash
uv run --with pytest pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q
```

Expected: FAIL with `missing script` because `rebuild_indexes.py` does not exist yet.

- [ ] **Step 3: Write the index/report rebuild script**

Create `skills/llm-knowledge-base/scripts/rebuild_indexes.py`:

```python
from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_dir, iter_markdown_files, parse_frontmatter, write_json, write_text


def load_pages(kb_root: Path) -> list[dict]:
    pages = []
    for path in iter_markdown_files(kb_root):
        metadata, _body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not metadata:
            continue
        pages.append(
            {
                "id": metadata.get("id", path.stem),
                "type": metadata.get("type", "unknown"),
                "title": metadata.get("title", path.stem.replace("-", " ").title()),
                "status": metadata.get("status", "draft"),
                "confidence": float(metadata.get("confidence", 0.0)),
                "source_refs": metadata.get("source_refs", []),
                "related_pages": metadata.get("related_pages", []),
                "path": path.relative_to(kb_root.parent).as_posix(),
            }
        )
    return pages


def render_index(pages: list[dict]) -> str:
    grouped: dict[str, list[dict]] = {}
    for page in pages:
        grouped.setdefault(page["type"], []).append(page)

    lines = [
        "# Knowledge Base Index",
        "",
        "## Page Counts",
    ]
    for page_type in sorted(grouped):
        lines.append(f"- `{page_type}`: {len(grouped[page_type])}")

    for page_type in sorted(grouped):
        lines.extend(["", f"## {page_type.title()} Pages"])
        for page in sorted(grouped[page_type], key=lambda item: item["title"]):
            lines.append(
                f"- [{page['title']}]({Path(page['path']).relative_to('kb').as_posix()}) "
                f"(`confidence: {page['confidence']:.2f}`, `status: {page['status']}`)"
            )

    return "\n".join(lines) + "\n"


def render_gap_report(pages: list[dict]) -> str:
    gap_pages = [page for page in pages if page["type"] == "open-question" or page["confidence"] < 0.7]
    lines = [
        "# Gap Report",
        "",
        "## Summary",
        f"- Total gap candidates: {len(gap_pages)}",
        "",
        "## Gap Candidates",
    ]
    for page in gap_pages:
        lines.append(f"- [{page['title']}](../../{page['path']}) (`type: {page['type']}`, `confidence: {page['confidence']:.2f}`)")
    return "\n".join(lines) + "\n"


def render_conflict_report(pages: list[dict]) -> str:
    conflict_pages = [page for page in pages if page["status"] == "conflict"]
    lines = [
        "# Conflict Report",
        "",
        "## Summary",
        f"- Total conflicts: {len(conflict_pages)}",
        "",
        "## Conflicts",
    ]
    for page in conflict_pages:
        lines.append(f"- [{page['title']}](../../{page['path']}) (`confidence: {page['confidence']:.2f}`)")
    return "\n".join(lines) + "\n"


def render_improvement_report(pages: list[dict]) -> str:
    weak_pages = [page for page in pages if page["type"] == "open-question" or page["confidence"] < 0.7]
    lines = [
        "# Improvement Report",
        "",
        "## Recommended Improvements",
    ]
    for page in weak_pages:
        lines.append(
            f"- Add or refine source material for [{page['title']}](../../{page['path']}) "
            f"because its current confidence is {page['confidence']:.2f}."
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild derived indexes and reports from kb markdown pages.")
    parser.add_argument("repo_root", help="Path to the repo root.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    pages = load_pages(repo_root / "kb")

    write_text(repo_root / "kb" / "index.md", render_index(pages), overwrite=True)

    reports_dir = ensure_dir(repo_root / "generated" / "reports")
    write_text(reports_dir / "gap-report.md", render_gap_report(pages), overwrite=True)
    write_text(reports_dir / "conflict-report.md", render_conflict_report(pages), overwrite=True)
    write_text(reports_dir / "improvement-report.md", render_improvement_report(pages), overwrite=True)

    link_map = {
        page["id"]: {
            "path": page["path"],
            "related_pages": page["related_pages"],
            "source_refs": page["source_refs"],
            "type": page["type"],
        }
        for page in pages
    }
    write_json(repo_root / ".kb-state" / "link-map.json", link_map)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the index rebuild test to verify it passes**

Run:

```bash
uv run --with pytest pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q
```

Expected: PASS with `1 passed`.

- [ ] **Step 5: Commit the index/report rebuilder**

Run:

```bash
git add \
  skills/llm-knowledge-base/scripts/rebuild_indexes.py \
  tests/skills/llm_knowledge_base/test_rebuild_indexes.py
git commit -m "feat: add kb index and report rebuilding"
```

Expected: a commit is created for index and report rebuilding.

### Task 6: Write the Skill Instructions, References, and Metadata

**Files:**
- Modify: `skills/llm-knowledge-base/SKILL.md`
- Modify: `skills/llm-knowledge-base/agents/openai.yaml`
- Create: `skills/llm-knowledge-base/references/repo-contract.md`
- Create: `skills/llm-knowledge-base/references/page-types.md`
- Create: `skills/llm-knowledge-base/references/provenance-and-confidence.md`
- Create: `skills/llm-knowledge-base/references/output-patterns.md`
- Create: `tests/skills/llm_knowledge_base/test_skill_docs.py`

- [ ] **Step 1: Write the failing skill-doc smoke test**

Create `tests/skills/llm_knowledge_base/test_skill_docs.py`:

```python
from pathlib import Path


SKILL = Path("skills/llm-knowledge-base/SKILL.md")
REFERENCES = [
    Path("skills/llm-knowledge-base/references/repo-contract.md"),
    Path("skills/llm-knowledge-base/references/page-types.md"),
    Path("skills/llm-knowledge-base/references/provenance-and-confidence.md"),
    Path("skills/llm-knowledge-base/references/output-patterns.md"),
]


def test_skill_doc_is_concrete_and_placeholder_free():
    text = SKILL.read_text(encoding="utf-8")
    assert "TODO" not in text
    assert "raw/" in text
    assert "kb/" in text
    assert "generated/" in text
    assert ".kb-state/" in text
    assert "update_manifest.py" in text
    assert "plan_ingestion.py" in text
    assert "rebuild_indexes.py" in text
    assert "If the request needs facts the KB does not support" in text


def test_reference_docs_exist():
    for reference_path in REFERENCES:
        assert reference_path.exists(), reference_path
```

- [ ] **Step 2: Run the skill-doc test to verify it fails**

Run:

```bash
uv run --with pytest pytest tests/skills/llm_knowledge_base/test_skill_docs.py -q
```

Expected: FAIL because `SKILL.md` still contains scaffold placeholders and the reference files do not exist yet.

- [ ] **Step 3: Write the reference docs**

Create `skills/llm-knowledge-base/references/repo-contract.md`:

```md
# Repo Contract

Treat the target repo as a split between evidence, policy, derived knowledge, and human-owned outputs.

- `knowledge-base.yaml` is human-owned policy.
- `raw/` is immutable source evidence.
- `kb/` is Codex-managed normalized knowledge.
- `generated/` is derived output safe to regenerate.
- `published/` is for human-maintained documents that should no longer be overwritten.
- `.kb-state/` stores manifests, plans, link maps, and ingestion history.

Never edit files in `raw/`.
Never hide missing information by filling it in silently.
Prefer regeneration of `kb/` and `generated/` over manual patching.
```

Create `skills/llm-knowledge-base/references/page-types.md`:

```md
# Page Types

Universal page types:

- `source`
- `concept`
- `procedure`
- `glossary-term`
- `decision`
- `open-question`
- `report`

Domain-specific page types come from `knowledge-base.yaml`.
If a recurring pattern does not fit the configured taxonomy, propose a candidate new type in `.kb-state/proposed-types.json` or a generated report rather than silently making it canonical.
Use the nearest configured type plus tags until a human approves the new type.
```

Create `skills/llm-knowledge-base/references/provenance-and-confidence.md`:

```md
# Provenance and Confidence

Every derived page should carry:

- at least one source reference when the claim is supported
- a confidence score
- a clear distinction between `fact`, `inference`, `editorial-normalization`, and `open-question`

Apply the configured confidence rubric conservatively.
Lower confidence when the evidence is sparse, conflicting, incomplete, or inferred.
If the request needs facts the KB does not support, say so directly and point to the missing page, source, or gap.
```

Create `skills/llm-knowledge-base/references/output-patterns.md`:

```md
# Output Patterns

Generate outputs from `kb/`, not directly from `raw/`.

Supported patterns:

- curriculum outlines
- lesson plans
- gap reports
- improvement reports
- policy drafts
- culture or culture-building documents

Every generated output should include a source basis section or equivalent citation map, should surface low-confidence sections, and should list any missing prerequisites that weaken the result.
```

- [ ] **Step 4: Replace the scaffolded SKILL.md with the real operator guide**

Replace `skills/llm-knowledge-base/SKILL.md` with:

```md
---
name: llm-knowledge-base
description: Bootstrap and maintain a codex-managed linked markdown knowledge base from raw source files plus root configuration. Use when Codex needs to create an "LLM wiki", ingest raw documents into a normalized knowledge base, track file hashes and ingestion state, rebuild indexes or reports, or generate downstream artifacts such as curriculum, lesson plans, gap reports, improvement reports, policy drafts, or culture documents while preserving provenance, confidence, and explicit missing-information handling.
---

# LLM Knowledge Base

## Overview

Use this skill to create and maintain a repo-local knowledge base that separates evidence in `raw/` from normalized knowledge in `kb/`, reproducible outputs in `generated/`, and operational state in `.kb-state/`.

If the request needs facts the KB does not support, do not invent them. Surface the missing information as an `open-question`, gap report entry, or direct explanation to the user.

## Quick Start

For a new repo:

```bash
python3 skills/llm-knowledge-base/scripts/init_repo.py .
```

For new or replaced raw files:

```bash
python3 skills/llm-knowledge-base/scripts/update_manifest.py .
python3 skills/llm-knowledge-base/scripts/plan_ingestion.py .
```

After adding or editing `kb/` pages:

```bash
python3 skills/llm-knowledge-base/scripts/rebuild_indexes.py .
```

## Repo Contract

Follow `references/repo-contract.md`.

- `knowledge-base.yaml` is human-owned policy.
- `raw/` is immutable evidence.
- `kb/` is Codex-managed normalized knowledge.
- `generated/` is reproducible output.
- `published/` is human-maintained output.
- `.kb-state/` is operational memory.

## Workflow

### 1. Bootstrap

Run `scripts/init_repo.py` at repo root to create the standard layout and starter state files.
Do not move config into `kb/`; keep `knowledge-base.yaml` at repo root because it is policy, not generated knowledge.

### 2. Detect raw-file changes

Users may copy or unzip files directly into `raw/`.
Run `scripts/update_manifest.py` to hash the current raw files and update `.kb-state/raw-manifest.json`.
Run `scripts/plan_ingestion.py` to separate files into `to_ingest`, `unchanged`, and `removed`.

Treat removed files as review items. Do not silently delete derived KB pages.

### 3. Normalize knowledge into `kb/`

Create atomic markdown pages in `kb/` using the templates in `assets/templates/pages/`.
Create one `source` page per raw artifact.
Break synthesized knowledge into small pages with explicit links and source references.

Use:

- `source.md` for source artifacts
- `knowledge-page.md` for `concept`, `procedure`, `glossary-term`, and `decision`
- `domain-page.md` for configured domain-specific page types
- `open-question.md` for missing or ambiguous information
- `report.md` for generated analytical outputs

### 4. Rebuild derived indexes and reports

After changing `kb/`, run `scripts/rebuild_indexes.py`.
This refreshes:

- `kb/index.md`
- `generated/reports/gap-report.md`
- `generated/reports/conflict-report.md`
- `.kb-state/link-map.json`

### 5. Generate downstream artifacts

Generate curriculum, lesson plans, policy drafts, culture docs, and reports from `kb/`, not directly from `raw/`.
Use `references/output-patterns.md` for output expectations.
Every generated artifact should surface provenance, confidence, and missing prerequisites.

## Page Types

Follow `references/page-types.md`.

Use universal page types for shared structure:

- `source`
- `concept`
- `procedure`
- `glossary-term`
- `decision`
- `open-question`
- `report`

Use domain-specific page types from `knowledge-base.yaml`.
If the taxonomy is insufficient, propose new types instead of silently making them canonical.

## Provenance and Confidence

Follow `references/provenance-and-confidence.md`.

Every substantive page should include:

- source references
- a confidence score
- a conservative distinction between fact and inference
- an explicit record of missing information when the evidence is incomplete

If two sources conflict, preserve both claims, reduce confidence, and create an `open-question` or conflict report entry.
```

- [ ] **Step 5: Regenerate the UI metadata**

Run:

```bash
python3 /Users/huan/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py \
  skills/llm-knowledge-base \
  --interface display_name="LLM Knowledge Base" \
  --interface short_description="Build and maintain linked LLM wikis" \
  --interface default_prompt="Use this skill to create or maintain a linked markdown knowledge base with provenance, confidence, and incremental ingestion."
```

Expected: `skills/llm-knowledge-base/agents/openai.yaml` is rewritten without placeholder content.

- [ ] **Step 6: Run the skill-doc smoke test**

Run:

```bash
uv run --with pytest pytest tests/skills/llm_knowledge_base/test_skill_docs.py -q
```

Expected: PASS with `2 passed`.

- [ ] **Step 7: Run the upstream skill validator**

Run:

```bash
uv run --with pyyaml python /Users/huan/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/llm-knowledge-base
```

Expected: output reports a valid skill structure and exits with status `0`.

- [ ] **Step 8: Commit the skill docs and metadata**

Run:

```bash
git add \
  skills/llm-knowledge-base/SKILL.md \
  skills/llm-knowledge-base/agents/openai.yaml \
  skills/llm-knowledge-base/references \
  tests/skills/llm_knowledge_base/test_skill_docs.py
git commit -m "feat: document llm knowledge base skill workflows"
```

Expected: a commit is created for the final skill guidance.

### Task 7: Run Full Verification

**Files:**
- Modify: none
- Test: `tests/skills/llm_knowledge_base/test_init_repo.py`
- Test: `tests/skills/llm_knowledge_base/test_update_manifest.py`
- Test: `tests/skills/llm_knowledge_base/test_plan_ingestion.py`
- Test: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`
- Test: `tests/skills/llm_knowledge_base/test_skill_docs.py`

- [ ] **Step 1: Run the complete skill test suite**

Run:

```bash
uv run --with pytest pytest tests/skills/llm_knowledge_base -q
```

Expected: PASS with all tests green.

- [ ] **Step 2: Re-run the upstream validator**

Run:

```bash
uv run --with pyyaml python /Users/huan/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/llm-knowledge-base
```

Expected: validator exits with status `0`.

- [ ] **Step 3: Commit the verified final state**

Run:

```bash
git add skills/llm-knowledge-base tests/skills/llm_knowledge_base
git commit -m "test: verify llm knowledge base skill"
```

Expected: the final verification commit records the tested skill state.
