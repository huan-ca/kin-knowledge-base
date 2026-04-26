# KIN Curriculum Filename Rollback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Revert generated curriculum filenames to the simple `week-xx-[doc-type].md` format and add top-level syllabus files plus per-file cycle/theme metadata blocks.

**Architecture:** Update the curriculum generator so filename construction returns to the simple stable pattern, while the richer cycle/theme metadata moves into the generated file body and three top-level syllabus files under `generated/curriculum/`. Keep the existing KB week data as the single source of truth for both the weekly files and the syllabus files.

**Tech Stack:** Python, markdown generation, KB week data in embedded JSON, pytest

---

### Task 1: Lock the rollback contract in tests

**Files:**
- Modify: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`

- [ ] **Step 1: Replace filename assertions with the simple pattern**

```python
assert (repo / "generated" / "curriculum" / "youth" / "week-01-curriculum.md").exists()
assert (repo / "generated" / "curriculum" / "adult" / "week-24-fully-scripted-session.md").exists()
assert (repo / "generated" / "curriculum" / "tots" / "week-12-coach-guide.md").exists()
```

- [ ] **Step 2: Add syllabus file assertions**

```python
assert (repo / "generated" / "curriculum" / "tots-syllabus.md").exists()
assert (repo / "generated" / "curriculum" / "youth-syllabus.md").exists()
assert (repo / "generated" / "curriculum" / "adult-syllabus.md").exists()
```

- [ ] **Step 3: Add content assertions for the metadata block**

```python
youth_text = (repo / "generated" / "curriculum" / "youth" / "week-01-curriculum.md").read_text(encoding="utf-8")
assert "- Cycle: defensive" in youth_text
assert "- Theme: Youth Theme 01" in youth_text
```

- [ ] **Step 4: Add content assertions for the syllabus**

```python
syllabus_text = (repo / "generated" / "curriculum" / "tots-syllabus.md").read_text(encoding="utf-8")
assert "| Week | Cycle | Theme | Description | Main Goal |" in syllabus_text
```

- [ ] **Step 5: Run the focused tests to verify they fail**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`
Expected: FAIL because the generator still emits bracketed filenames and no syllabus files.

### Task 2: Implement the generator rollback and syllabus generation

**Files:**
- Modify: `skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`

- [ ] **Step 1: Remove the bracketed filename builder logic**

```python
def build_output_filename(week: dict, output_type: str) -> str:
    week_number = int(week["week"])
    return f"week-{week_number:02d}-{output_type}.md"
```

- [ ] **Step 2: Keep `fully-scripted-session` as the filename label again**

```python
OUTPUT_TYPES = (
    "curriculum",
    "quick-outline",
    "coach-guide",
    "fully-scripted-session",
)
```

- [ ] **Step 3: Add a reusable metadata block renderer**

```python
def render_metadata_block(program: str, week: dict) -> list[str]:
    ...
```

It should include the required top-of-file fields from the spec.

- [ ] **Step 4: Inject that metadata block near the top of every weekly renderer**

The block should appear immediately under the `# ...` title and before the rest of the weekly content.

- [ ] **Step 5: Add syllabus rendering**

```python
def render_program_syllabus(program: str, weeks: list[dict]) -> str:
    ...
```

It should write:
- `generated/curriculum/tots-syllabus.md`
- `generated/curriculum/youth-syllabus.md`
- `generated/curriculum/adult-syllabus.md`

- [ ] **Step 6: Run the focused tests to verify they pass**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`
Expected: PASS

- [ ] **Step 7: Run the full knowledge-base suite**

Run: `pytest tests/skills/llm_knowledge_base -q`
Expected: PASS

### Task 3: Regenerate outputs and verify the new structure

**Files:**
- Modify: `generated/curriculum/tots/*.md`
- Modify: `generated/curriculum/youth/*.md`
- Modify: `generated/curriculum/adult/*.md`
- Create: `generated/curriculum/tots-syllabus.md`
- Create: `generated/curriculum/youth-syllabus.md`
- Create: `generated/curriculum/adult-syllabus.md`

- [ ] **Step 1: Run the generator**

Run: `python3 skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py .`
Expected: simple filenames are regenerated and the three syllabus files appear.

- [ ] **Step 2: Verify example weekly filenames**

Run: `find generated/curriculum/tots -maxdepth 1 -type f | sed 's#^.*/##' | sort | head -8`
Expected: names like `week-01-coach-guide.md`, `week-01-curriculum.md`, `week-01-fully-scripted-session.md`, `week-01-quick-outline.md`

- [ ] **Step 3: Verify syllabus files exist**

Run: `find generated/curriculum -maxdepth 1 -type f | sed 's#^.*/##' | sort`
Expected: includes `adult-syllabus.md`, `tots-syllabus.md`, `youth-syllabus.md`

- [ ] **Step 4: Verify counts**

Run: `find generated/curriculum/tots -name '*.md' | wc -l`
Expected: `48`

Run: `find generated/curriculum/youth -name '*.md' | wc -l`
Expected: `96`

Run: `find generated/curriculum/adult -name '*.md' | wc -l`
Expected: `96`

- [ ] **Step 5: Verify metadata block and syllabus content**

Run: `sed -n '1,40p' generated/curriculum/youth/week-01-curriculum.md`
Expected: top metadata block includes cycle and theme.

Run: `sed -n '1,80p' generated/curriculum/youth-syllabus.md`
Expected: intro plus week map containing cycle, theme, description, and main goal.

### Task 4: Final verification and handoff

**Files:**
- Modify: none
- Test: full verification commands

- [ ] **Step 1: Run full verification fresh**

Run: `python3 skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py . && pytest tests/skills/llm_knowledge_base -q`
Expected: generator completes and tests pass.

- [ ] **Step 2: Verify clean tree**

Run: `git status --short`
Expected: clean working tree after committing.

- [ ] **Step 3: Summarize residual risk**

Report:
- syllabus prose is generated from existing KB week data, so any future KB wording changes will propagate directly
- tots cycles remain in the KB for syllabus and metadata use even though they no longer affect filenames
