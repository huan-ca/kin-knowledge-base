# KIN BJJ Weekly Curriculum Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the missing KB week-map layer and generate reproducible weekly curriculum plus lesson-plan markdown files for tots, youth, and adult programs under `generated/`.

**Architecture:** Add explicit curriculum-unit KB pages that capture the approved weekly sequencing and program-specific structures, then add a dedicated generator script that reads those KB pages, normalizes week records into structured in-memory data, and writes program/week/type markdown files under `generated/curriculum/`. Keep index rebuilding separate by continuing to use the existing `rebuild_indexes.py` script after KB changes.

**Tech Stack:** Python scripts, markdown KB pages with frontmatter, pytest, existing `skills/llm-knowledge-base/scripts/common.py` helpers

---

### Task 1: Add generator test coverage first

**Files:**
- Create: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`
- Modify: none
- Test: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`

- [ ] **Step 1: Write the failing test**

```python
def test_generate_curriculum_outputs_creates_expected_program_directories_and_week_files(tmp_path):
    ...
    subprocess.run([sys.executable, str(GENERATE_SCRIPT), str(repo)], check=True)
    assert (repo / "generated" / "curriculum" / "youth" / "week-01-curriculum.md").exists()
    assert (repo / "generated" / "curriculum" / "adult" / "week-24-fully-scripted-session.md").exists()
    assert (repo / "generated" / "curriculum" / "tots" / "week-12-coach-guide.md").exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`
Expected: FAIL because `generate_curriculum_outputs.py` does not exist yet.

- [ ] **Step 3: Add a second failing test for file content shape**

```python
def test_generate_curriculum_outputs_includes_level_sections_and_program_specific_notes(tmp_path):
    ...
    youth_text = (repo / "generated" / "curriculum" / "youth" / "week-01-curriculum.md").read_text(encoding="utf-8")
    adult_text = (repo / "generated" / "curriculum" / "adult" / "week-01-curriculum.md").read_text(encoding="utf-8")
    tots_text = (repo / "generated" / "curriculum" / "tots" / "week-01-curriculum.md").read_text(encoding="utf-8")
    assert "## Level 1" in youth_text
    assert "## Level 2" in youth_text
    assert "## Adult-Specific Notes" in adult_text
    assert "## Movement Theme" in tots_text
```

- [ ] **Step 4: Run the test file again**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`
Expected: FAIL with missing script or missing output behavior.

- [ ] **Step 5: Commit**

```bash
git add tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py
git commit -m "test: add curriculum output generator coverage"
```

### Task 2: Add KB week-map pages and resolve the sequencing gap

**Files:**
- Create: `kb/curriculum/youth-24-week-theme-map.md`
- Create: `kb/curriculum/adult-24-week-theme-map.md`
- Create: `kb/curriculum/tots-12-week-theme-map.md`
- Modify: `kb/open-questions/week-by-week-curriculum-sequence.md`
- Test: `pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`

- [ ] **Step 1: Add the youth week-map page**

```markdown
---
id: youth-24-week-theme-map
type: curriculum-unit
title: "Youth 24-Week Theme Map"
status: active
confidence: 0.65
claim_label: editorial-normalization
source_refs:
- source-high-level-overview#chunk-001
- source-kin-bjj-compendium#chunk-010
related_pages:
- youth-24-week-curriculum-framework
---
```

- [ ] **Step 2: Add the adult and tots week-map pages**

```markdown
---
id: adult-24-week-theme-map
type: curriculum-unit
...
---
```

```markdown
---
id: tots-12-week-theme-map
type: curriculum-unit
...
---
```

- [ ] **Step 3: Mark the sequencing open question as resolved by the new week maps**

```markdown
## Resolution Status
- This question is resolved by the proposed youth, adult, and tots theme-map pages created from source-backed framework plus approved client guidance.
```

- [ ] **Step 4: Run the generator test file**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`
Expected: still FAIL because the generator script has not been implemented yet.

- [ ] **Step 5: Commit**

```bash
git add kb/curriculum/youth-24-week-theme-map.md kb/curriculum/adult-24-week-theme-map.md kb/curriculum/tots-12-week-theme-map.md kb/open-questions/week-by-week-curriculum-sequence.md
git commit -m "docs: add KIN weekly curriculum theme maps"
```

### Task 3: Implement the curriculum output generator

**Files:**
- Create: `skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py`
- Modify: `skills/llm-knowledge-base/scripts/common.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`

- [ ] **Step 1: Add a small helper for parsing structured week blocks if needed**

```python
def parse_bulleted_fields(lines: list[str]) -> dict[str, list[str]]:
    ...
```

- [ ] **Step 2: Implement the generator script**

```python
def main() -> None:
    parser = argparse.ArgumentParser(...)
    parser.add_argument("repo_root", help="Path to the repo root.")
    ...
    generate_outputs(repo_root)
```

The script should:
- load the three theme-map KB pages
- parse week sections into structured records
- render four output types per week
- write files under `generated/curriculum/<program>/`

- [ ] **Step 3: Run the new tests**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`
Expected: PASS

- [ ] **Step 4: Run the existing knowledge-base tests**

Run: `pytest tests/skills/llm_knowledge_base -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add skills/llm-knowledge-base/scripts/common.py skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py
git commit -m "feat: generate weekly curriculum outputs from KB"
```

### Task 4: Generate outputs and refresh derived artifacts

**Files:**
- Modify: `generated/curriculum/tots/*.md`
- Modify: `generated/curriculum/youth/*.md`
- Modify: `generated/curriculum/adult/*.md`
- Modify: `kb/index.md`
- Modify: `generated/reports/gap-report.md`
- Modify: `generated/reports/conflict-report.md`
- Modify: `generated/reports/improvement-report.md`
- Modify: `.kb-state/link-map.json`
- Test: runtime verification commands

- [ ] **Step 1: Run the generator**

Run: `python skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py .`
Expected: generated curriculum directories and weekly markdown files appear.

- [ ] **Step 2: Rebuild indexes and reports**

Run: `python skills/llm-knowledge-base/scripts/rebuild_indexes.py .`
Expected: `kb/index.md`, reports, and `.kb-state/link-map.json` update successfully.

- [ ] **Step 3: Verify output counts**

Run: `find generated/curriculum/tots -name '*.md' | wc -l`
Expected: `48`

Run: `find generated/curriculum/youth -name '*.md' | wc -l`
Expected: `96`

Run: `find generated/curriculum/adult -name '*.md' | wc -l`
Expected: `96`

- [ ] **Step 4: Verify key content invariants**

Run: `rg -n "Self-Defense|Adult-Specific Notes|Movement Theme|Level 1|Level 2" generated/curriculum`
Expected: matches confirm youth self-defense weeks, adult notes, tots structure, and level sections are present.

- [ ] **Step 5: Commit**

```bash
git add generated/curriculum kb/index.md generated/reports .kb-state/link-map.json
git commit -m "feat: generate KIN weekly curriculum artifacts"
```

### Task 5: Final verification and handoff

**Files:**
- Modify: none
- Test: full verification commands

- [ ] **Step 1: Run the generator and tests fresh**

Run: `python skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py . && pytest tests/skills/llm_knowledge_base -q`
Expected: generator completes and test suite passes.

- [ ] **Step 2: Verify git status**

Run: `git status --short`
Expected: clean working tree.

- [ ] **Step 3: Summarize residual risk**

Report:
- week sequencing is still a proposed editorial normalization
- generated lesson-plan text is framework quality, not human-client-polished final prose

- [ ] **Step 4: Commit if needed**

```bash
git add -A
git commit -m "chore: finalize weekly curriculum generation"
```
