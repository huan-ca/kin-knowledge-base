# KB Manifest Location Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the canonical KB manifest from `generated/kb-manifest.json` to `kb/kb-manifest.json`.

**Architecture:** Keep the manifest schema unchanged and only move the output boundary. Update `rebuild_indexes.py` to write the manifest into `kb/`, update rebuild tests to expect the new location, and rebuild the real repo outputs so the checked-in manifest matches the new contract.

**Tech Stack:** Python 3, pytest, repo-local rebuild script

---

### Task 1: Add failing tests for the new manifest location

**Files:**
- Modify: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`
- Test: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`

- [ ] **Step 1: Change the primary rebuild test to read from `kb/kb-manifest.json`**

```python
    kb_manifest = json.loads((repo / "kb" / "kb-manifest.json").read_text(encoding="utf-8"))
```

- [ ] **Step 2: Add an assertion that the old generated-path file does not exist**

```python
    assert not (repo / "generated" / "kb-manifest.json").exists()
```

- [ ] **Step 3: Run the focused rebuild test to confirm current failure**

Run: `pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q`

Expected: FAIL because the rebuild script still writes only `generated/kb-manifest.json`.

- [ ] **Step 4: Commit the red-test checkpoint**

```bash
git add tests/skills/llm_knowledge_base/test_rebuild_indexes.py
git commit -m "test: cover kb manifest location change"
```

### Task 2: Move the manifest output boundary in the rebuild script

**Files:**
- Modify: `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
- Test: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`

- [ ] **Step 1: Change the manifest write path from `generated/` to `kb/`**

```python
    write_json(repo_root / "kb" / "kb-manifest.json", build_kb_manifest(pages))
```

- [ ] **Step 2: Remove the old generated-path write**

```python
# delete:
write_json(repo_root / "generated" / "kb-manifest.json", build_kb_manifest(pages))
```

- [ ] **Step 3: Run the focused rebuild tests**

Run: `pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q`

Expected: PASS

- [ ] **Step 4: Commit the implementation**

```bash
git add skills/llm-knowledge-base/scripts/rebuild_indexes.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py
git commit -m "feat: move kb manifest into kb directory"
```

### Task 3: Verify and rebuild the real repo outputs

**Files:**
- Create: `kb/kb-manifest.json`
- Delete or stop updating: `generated/kb-manifest.json`
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

Expected:
- `kb/index.md` updated
- `kb/kb-manifest.json` written
- `generated/reports/gap-report.md` updated
- `generated/reports/conflict-report.md` updated
- `generated/reports/improvement-report.md` updated
- `.kb-state/link-map.json` updated

- [ ] **Step 4: Verify the new and old manifest locations**

Checklist:
- `kb/kb-manifest.json` exists
- `generated/kb-manifest.json` is absent or no longer relied on
- the manifest content still includes `page_counts` and `pages`

- [ ] **Step 5: Commit regenerated outputs if they changed**

```bash
git add skills/llm-knowledge-base/scripts/rebuild_indexes.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py kb/kb-manifest.json kb/index.md generated/reports/gap-report.md generated/reports/conflict-report.md generated/reports/improvement-report.md .kb-state/link-map.json
git commit -m "chore: rebuild kb manifest in kb directory"
```
