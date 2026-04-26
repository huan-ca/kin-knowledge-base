# KIN Curriculum Filename Convention Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the curriculum generator and supporting KB data so generated filenames follow the approved human-browsable bracketed naming convention.

**Architecture:** Add explicit cycle labels to the tots week-map KB data, centralize filename construction inside `generate_curriculum_outputs.py`, and update the generator tests to assert the new pattern directly. Regenerate the curriculum tree instead of manually renaming files so the output stays reproducible.

**Tech Stack:** Python, markdown KB pages with embedded JSON, pytest, generated markdown artifacts

---

### Task 1: Lock the new filename contract in tests

**Files:**
- Modify: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`

- [ ] **Step 1: Write the failing filename assertions**

```python
assert (repo / "generated" / "curriculum" / "youth" / "week-01_[defensive]_[youth-theme-01]_[curriculum].md").exists()
assert (repo / "generated" / "curriculum" / "adult" / "week-24_[offensive]_[adult-lower-body-defense]_[scripted-session].md").exists()
assert (repo / "generated" / "curriculum" / "tots" / "week-12_[review]_[tots-theme-12]_[coach-guide].md").exists()
```

- [ ] **Step 2: Add content-read assertions that use the new filenames**

```python
youth_text = (
    repo / "generated" / "curriculum" / "youth" / "week-01_[defensive]_[youth-theme-01]_[curriculum].md"
).read_text(encoding="utf-8")
adult_text = (
    repo / "generated" / "curriculum" / "adult" / "week-01_[defensive]_[adult-theme-01]_[curriculum].md"
).read_text(encoding="utf-8")
tots_text = (
    repo / "generated" / "curriculum" / "tots" / "week-01_[foundation]_[tots-theme-01]_[curriculum].md"
).read_text(encoding="utf-8")
```

- [ ] **Step 3: Run the focused tests to verify they fail**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`
Expected: FAIL because the generator still emits the old filename pattern.

- [ ] **Step 4: Commit the red test change after review if you want a checkpoint**

```bash
git add tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py
git commit -m "test: assert curriculum filename convention"
```

### Task 2: Add explicit tots cycle labels to the KB week data

**Files:**
- Modify: `kb/curriculum/tots-12-week-theme-map.md`
- Test: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`

- [ ] **Step 1: Add a `cycle` field to each tots week record**

```json
{
  "week": 1,
  "cycle": "foundation",
  "theme": "Mat Rules, Base, And Ready Stance",
  ...
}
```

Suggested cycle labels for the existing weeks:
- weeks 1-4: `foundation`
- weeks 5-8: `movement`
- weeks 9-11: `partner`
- week 12: `review`

- [ ] **Step 2: Keep the rest of the week payload untouched**

No other field names should change in this task.

- [ ] **Step 3: Run the focused tests again**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`
Expected: still FAIL because the generator has not adopted the new naming convention yet.

- [ ] **Step 4: Commit if you want a checkpoint**

```bash
git add kb/curriculum/tots-12-week-theme-map.md
git commit -m "docs: add tots filename cycle labels"
```

### Task 3: Implement centralized filename generation

**Files:**
- Modify: `skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`

- [ ] **Step 1: Add a slug helper and filename builder**

```python
def slugify(value: str) -> str:
    ...


def build_output_filename(week: dict, output_type: str) -> str:
    week_number = int(week["week"])
    cycle = slugify(str(week.get("cycle", "unspecified")))
    theme_slug = slugify(str(week["theme"]))
    file_type = {
        "fully-scripted-session": "scripted-session",
        "quick-outline": "quick-outline",
        "coach-guide": "coach-guide",
        "curriculum": "curriculum",
    }[output_type]
    return f"week-{week_number:02d}_[{cycle}]_[{theme_slug}]_[{file_type}].md"
```

- [ ] **Step 2: Replace the old filename construction with the builder**

```python
filename = build_output_filename(week, output_type)
```

- [ ] **Step 3: Keep the markdown content titles untouched**

The change is about filenames, not document titles.

- [ ] **Step 4: Run the focused tests to verify they pass**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`
Expected: PASS

- [ ] **Step 5: Run the full knowledge-base test suite**

Run: `pytest tests/skills/llm_knowledge_base -q`
Expected: PASS

- [ ] **Step 6: Commit the implementation**

```bash
git add skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py
git commit -m "feat: apply curriculum filename convention"
```

### Task 4: Regenerate outputs and refresh derived files

**Files:**
- Modify: `generated/curriculum/tots/*.md`
- Modify: `generated/curriculum/youth/*.md`
- Modify: `generated/curriculum/adult/*.md`

- [ ] **Step 1: Run the generator**

Run: `python3 skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py .`
Expected: old files are replaced by the new bracketed filenames.

- [ ] **Step 2: Verify example filenames exist**

Run: `find generated/curriculum -maxdepth 2 -type f | sort | head -20`
Expected: filenames start with patterns such as `week-01_[defensive]_...` and `week-01_[foundation]_...`.

- [ ] **Step 3: Verify file counts remain unchanged**

Run: `find generated/curriculum/tots -name '*.md' | wc -l`
Expected: `48`

Run: `find generated/curriculum/youth -name '*.md' | wc -l`
Expected: `96`

Run: `find generated/curriculum/adult -name '*.md' | wc -l`
Expected: `96`

- [ ] **Step 4: Verify no old filename pattern remains**

Run: `find generated/curriculum -name 'week-*-curriculum.md' -o -name 'week-*-coach-guide.md' -o -name 'week-*-fully-scripted-session.md' -o -name 'week-*-quick-outline.md'`
Expected: no output

- [ ] **Step 5: Commit regenerated outputs**

```bash
git add generated/curriculum
git commit -m "chore: regenerate curriculum filenames"
```

### Task 5: Final verification and branch handoff

**Files:**
- Modify: none
- Test: full verification commands

- [ ] **Step 1: Run full verification fresh**

Run: `python3 skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py . && pytest tests/skills/llm_knowledge_base -q`
Expected: generator completes and tests pass.

- [ ] **Step 2: Verify the worktree is clean**

Run: `git status --short`
Expected: clean working tree.

- [ ] **Step 3: Summarize residual risk**

Report:
- future theme or cycle wording changes will rename files by design
- brackets improve browsing but remain noisier for shell usage

- [ ] **Step 4: Commit any final docs changes if needed**

```bash
git add -A
git commit -m "chore: finalize curriculum filename convention"
```
