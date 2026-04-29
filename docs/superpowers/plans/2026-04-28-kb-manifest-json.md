# KB Manifest JSON Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a machine-readable `generated/kb-manifest.json` companion artifact to the KB rebuild flow.

**Architecture:** Extend `skills/llm-knowledge-base/scripts/rebuild_indexes.py` so the same validated page inventory currently used for `kb/index.md` also emits a deterministic JSON manifest under `generated/`. Add focused rebuild tests that assert file creation, required fields, and stable structure.

**Tech Stack:** Python 3, pytest, repo-local rebuild script

---

### Task 1: Add failing tests for the JSON manifest artifact

**Files:**
- Modify: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`
- Test: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`

- [ ] **Step 1: Extend the main rebuild test to load `generated/kb-manifest.json`**

```python
    kb_manifest = json.loads((repo / "generated" / "kb-manifest.json").read_text(encoding="utf-8"))
```

- [ ] **Step 2: Add assertions for top-level manifest structure and required page fields**

```python
    assert kb_manifest["page_counts"]["concept"] == 4
    assert isinstance(kb_manifest["pages"], list)

    closed_guard_record = next(page for page in kb_manifest["pages"] if page["id"] == "closed-guard")
    assert closed_guard_record["type"] == "concept"
    assert closed_guard_record["title"] == "Closed Guard"
    assert closed_guard_record["status"] == "active"
    assert closed_guard_record["confidence"] == 0.9
    assert closed_guard_record["path"] == "kb/concepts/closed-guard.md"
    assert closed_guard_record["claim_label"] == "fact"
    assert closed_guard_record["source_refs"] == ["source-compendium#chunk-001", "source-compendium#chunk-009"]
    assert closed_guard_record["related_pages"] == ["armbar", "triangle-choke"]
```

- [ ] **Step 3: Add a deterministic ordering assertion**

```python
    manifest_page_ids = [page["id"] for page in kb_manifest["pages"]]
    assert manifest_page_ids == sorted(manifest_page_ids, key=str)
```

- [ ] **Step 4: Run the focused rebuild test to confirm current failure**

Run: `pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q`

Expected: FAIL because `generated/kb-manifest.json` does not exist yet.

- [ ] **Step 5: Commit the red-test checkpoint**

```bash
git add tests/skills/llm_knowledge_base/test_rebuild_indexes.py
git commit -m "test: cover kb manifest json output"
```

### Task 2: Emit the JSON manifest from the rebuild script

**Files:**
- Modify: `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
- Test: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`

- [ ] **Step 1: Add a helper that renders the manifest payload from the validated page list**

```python
def build_kb_manifest(pages: list[dict]) -> dict:
    page_counts: dict[str, int] = {}
    for page in pages:
        page_counts[page["type"]] = page_counts.get(page["type"], 0) + 1

    manifest_pages = [
        {
            "id": page["id"],
            "type": page["type"],
            "title": page["title"],
            "status": page["status"],
            "confidence": page["confidence"],
            "path": page["path"],
            "claim_label": page["claim_label"],
            "source_refs": page["source_refs"],
            "related_pages": page["related_pages"],
        }
        for page in sorted(pages, key=lambda item: item["id"])
    ]
    return {
        "page_counts": dict(sorted(page_counts.items())),
        "pages": manifest_pages,
    }
```

- [ ] **Step 2: Write the manifest in `main()` after `kb/index.md` and reports are generated**

```python
    write_json(repo_root / "generated" / "kb-manifest.json", build_kb_manifest(pages))
```

- [ ] **Step 3: Keep the manifest boundary out of `.kb-state/`**

```python
# do not add this file under .kb-state; keep only:
write_json(repo_root / "generated" / "kb-manifest.json", ...)
```

- [ ] **Step 4: Run the focused rebuild test**

Run: `pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q`

Expected: PASS

- [ ] **Step 5: Commit the implementation**

```bash
git add skills/llm-knowledge-base/scripts/rebuild_indexes.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py
git commit -m "feat: emit kb manifest json"
```

### Task 3: Verify against the real repo state

**Files:**
- Modify: `generated/kb-manifest.json`
- Modify: `kb/index.md`
- Modify: `generated/reports/gap-report.md`
- Modify: `generated/reports/conflict-report.md`
- Modify: `generated/reports/improvement-report.md`

- [ ] **Step 1: Run the broader verification set**

Run: `pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py tests/skills/llm_knowledge_base/test_update_manifest.py tests/skills/llm_knowledge_base/test_plan_ingestion.py -q`

Expected: PASS

- [ ] **Step 2: Run bytecode verification**

Run: `python3 -m py_compile skills/llm-knowledge-base/scripts/rebuild_indexes.py`

Expected: no output

- [ ] **Step 3: Rebuild the real indexes**

Run: `python3 skills/llm-knowledge-base/scripts/rebuild_indexes.py .`

Expected: writes:
- `kb/index.md`
- `generated/kb-manifest.json`
- `generated/reports/gap-report.md`
- `generated/reports/conflict-report.md`
- `generated/reports/improvement-report.md`
- `.kb-state/link-map.json`

- [ ] **Step 4: Manually inspect the manifest**

Checklist:
- `generated/kb-manifest.json` exists
- it contains `page_counts`
- it contains `pages`
- one known page record includes `id`, `type`, `title`, `status`, `confidence`, and `path`
- the path values point at KB markdown files

- [ ] **Step 5: Commit regenerated outputs if they changed**

```bash
git add skills/llm-knowledge-base/scripts/rebuild_indexes.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py generated/kb-manifest.json kb/index.md generated/reports/gap-report.md generated/reports/conflict-report.md generated/reports/improvement-report.md .kb-state/link-map.json
git commit -m "chore: rebuild kb manifest outputs"
```
