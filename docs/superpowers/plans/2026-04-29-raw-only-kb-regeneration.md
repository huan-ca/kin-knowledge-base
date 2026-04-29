# Raw-Only KB Regeneration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the `kb/` tree from the current `raw/` files only, preserve example lesson markdown format in source pages, and enrich the JSON manifest with `summary` and `keywords` for lookup agents.

**Architecture:** Execute this as a raw-only normalization pass in an isolated worktree. First extend rebuild-time metadata and tests so the manifest can carry lookup-friendly fields. Then reconstruct `kb/` manually from the seven active raw files: source pages first, derived pages second, open questions where support ends, and finally rebuild indexes/reports/manifest from the regenerated KB state.

**Tech Stack:** Python 3, pytest, markdown KB pages, repo-local `llm-knowledge-base` scripts

---

### File Structure

**Files to modify**
- `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
- `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`

**Files to create or recreate under `kb/`**
- `kb/sources/*.md`
- `kb/concepts/*.md`
- `kb/procedures/*.md`
- `kb/class-types/*.md`
- `kb/programs/*.md`
- `kb/policies/*.md`
- `kb/position/*.md`
- `kb/lessons/*.md`
- `kb/values/*.md`
- `kb/open-questions/*.md`
- `kb/index.md` (rebuilt by script)

**Files to refresh**
- `generated/reports/gap-report.md`
- `generated/reports/conflict-report.md`
- `generated/reports/improvement-report.md`
- `generated/kb-manifest.json`
- `.kb-state/link-map.json`

**Source inputs to normalize**
- `raw/KIN BJJ Compendium.md`
- `raw/KIN BJJ kids lesson plan structure.md`
- `raw/high level overview.md`
- `raw/the_four_layers_of_bjj_skills_development.md`
- `raw/example_scripted_lesson_plan_adult.md`
- `raw/example_scripted_lesson_plan_youth.md`
- `raw/example_scripted_lesson_plan_tots.md`

### Task 1: Add Failing Tests For Manifest `summary` Support

**Files:**
- Modify: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`
- Modify later: `skills/llm-knowledge-base/scripts/rebuild_indexes.py`

- [ ] **Step 1: Extend the existing rebuild fixture page with a `summary` field**

Update the `closed-guard` fixture in `test_rebuild_indexes_creates_index_gap_report_conflict_report_and_link_map`:

```python
    concept_page.write_text(
        """---
id: closed-guard
type: concept
title: Closed Guard
status: active
confidence: 0.9
claim_label: fact
source_refs: [source-compendium#chunk-001, source-compendium#chunk-009]
related_pages: [armbar, triangle-choke]
domain_tags: [guard, offensive-cycle]
keywords: [closed guard, posture breaking, hip control]
summary: Closed guard is treated as a control and attack platform built on posture disruption, hip control, and connected sweep or submission threats.
---
# Closed Guard
""",
        encoding="utf-8",
    )
```

- [ ] **Step 2: Add failing manifest assertions for `summary`**

Extend the assertions:

```python
    assert closed_guard_record["summary"] == (
        "Closed guard is treated as a control and attack platform built on posture disruption, "
        "hip control, and connected sweep or submission threats."
    )
    armbar_record = next(page for page in kb_manifest["pages"] if page["id"] == "armbar")
    assert armbar_record["summary"] == ""
    assert link_map["closed-guard"]["summary"] == (
        "Closed guard is treated as a control and attack platform built on posture disruption, "
        "hip control, and connected sweep or submission threats."
    )
```

- [ ] **Step 3: Add a failing validation test showing `summary` must be a string when present**

Add a new parametrized case near the existing metadata validation tests:

```python
        (
            "summary-not-string",
            "id: summary-not-string\n"
            "type: concept\n"
            "title: Summary Not String\n"
            "status: active\n"
            "confidence: 0.5\n"
            "claim_label: fact\n"
            "source_refs: [source-a#chunk-001]\n"
            "related_pages: []\n"
            "summary:\n"
            "  - not-a-string\n",
            "summary must be a string in kb/concepts/summary-not-string.md",
        ),
```

- [ ] **Step 4: Run the rebuild test file and confirm it fails on missing `summary` support**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q
```

Expected:

```text
FAIL ... KeyError: 'summary' or validation mismatch for summary handling
```

- [ ] **Step 5: Commit the red test checkpoint**

```bash
git add tests/skills/llm_knowledge_base/test_rebuild_indexes.py
git commit -m "test: cover kb manifest summaries"
```

### Task 2: Implement Manifest `summary` Support

**Files:**
- Modify: `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
- Reuse tests from: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`

- [ ] **Step 1: Add optional `summary` parsing in `validate_page_metadata()`**

Insert after `keywords` validation:

```python
    summary = metadata.get("summary", "")
    if not isinstance(summary, str):
        raise ValueError(f"summary must be a string in {relative_path}")
```

Return it from the validated payload:

```python
        "domain_tags": domain_tags,
        "keywords": keywords,
        "summary": summary,
```

- [ ] **Step 2: Add `summary` to the KB manifest payload**

Update `build_kb_manifest()`:

```python
            "related_pages": page["related_pages"],
            "domain_tags": page["domain_tags"],
            "keywords": page["keywords"],
            "summary": page["summary"],
```

- [ ] **Step 3: Add `summary` to `.kb-state/link-map.json`**

Update the `link_map` record:

```python
            "type": page["type"],
            "domain_tags": page["domain_tags"],
            "keywords": page["keywords"],
            "summary": page["summary"],
```

- [ ] **Step 4: Run the targeted rebuild tests**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q
```

Expected:

```text
all tests in the file pass
```

- [ ] **Step 5: Commit the implementation checkpoint**

```bash
git add skills/llm-knowledge-base/scripts/rebuild_indexes.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py
git commit -m "feat: add kb manifest summaries"
```

### Task 3: Recreate Source Pages From Current Raw Files

**Files:**
- Create: `kb/sources/kin-bjj-compendium.md`
- Create: `kb/sources/kin-bjj-kids-lesson-plan-structure.md`
- Create: `kb/sources/high-level-overview.md`
- Create: `kb/sources/the-four-layers-of-bjj-skills-development.md`
- Create: `kb/sources/example-scripted-lesson-plan-adult.md`
- Create: `kb/sources/example-scripted-lesson-plan-youth.md`
- Create: `kb/sources/example-scripted-lesson-plan-tots.md`

- [ ] **Step 1: Recreate the four prose-heavy source pages with dense extracted detail**

For each of these files:

```text
kb/sources/kin-bjj-compendium.md
kb/sources/kin-bjj-kids-lesson-plan-structure.md
kb/sources/high-level-overview.md
kb/sources/the-four-layers-of-bjj-skills-development.md
```

Use frontmatter shaped like:

```md
---
id: source-kin-bjj-compendium
type: source
title: "KIN BJJ Compendium"
status: active
confidence: 1.0
source_refs: []
related_pages: []
domain_tags: [source, curriculum, technique]
keywords: [KIN BJJ compendium, curriculum, positions, submissions, escapes]
summary: Master source page for the compendium material, covering technical systems, teaching principles, training ideas, and program context used by the KB.
---
```

Then include:

```md
# KIN BJJ Compendium

## Source Summary
- ...

## Major Sections
- ...

## Extracted Claims
- ...

## Notes
- ...
```

- [ ] **Step 2: Recreate the three example source pages with preserved markdown format**

For:

```text
kb/sources/example-scripted-lesson-plan-adult.md
kb/sources/example-scripted-lesson-plan-youth.md
kb/sources/example-scripted-lesson-plan-tots.md
```

Use frontmatter like:

```md
---
id: source-example-scripted-lesson-plan-adult
type: source
title: "Example Scripted Lesson Plan Adult"
status: active
confidence: 1.0
source_refs: []
related_pages: []
domain_tags: [source, lesson-format, adult]
keywords: [example scripted lesson plan, adult class format, coach script]
summary: Example adult lesson-plan source showing the desired coach-facing markdown structure, section ordering, and instructional formatting.
---
```

And include:

```md
# Example Scripted Lesson Plan Adult

## Source Summary
- ...

## Format Signals
- ...

## Preserved Example Format

```markdown
... exact fenced example body from raw/example_scripted_lesson_plan_adult.md ...
```
```

Apply the same pattern to youth and tots.

- [ ] **Step 3: Verify source-page IDs and manifest alignment**

Run:

```bash
rg -n "^id: source-" kb/sources
```

Expected:

```text
one source page id per active raw file, all unique
```

- [ ] **Step 4: Commit the source-page regeneration checkpoint**

```bash
git add kb/sources
git commit -m "feat: regenerate kb source pages from raw inputs"
```

### Task 4: Rebuild Core Concept, Position, Policy, And Program Pages

**Files:**
- Create: `kb/concepts/*.md`
- Create: `kb/position/*.md`
- Create: `kb/policies/*.md`
- Create: `kb/programs/*.md`
- Create: `kb/values/*.md`

- [ ] **Step 1: Recreate the concept pages supported by the raw corpus**

Create or recreate concept pages with dense bodies and retrieval metadata for topics such as:

```text
kb/concepts/basic-bjj-match-strategy.md
kb/concepts/community-and-recognition-principles.md
kb/concepts/escape-framework.md
kb/concepts/four-layers-of-bjj-skill-development.md
kb/concepts/general-physical-preparedness-framework.md
kb/concepts/ibjjf-points-and-advantages-basics.md
kb/concepts/intuition-through-pattern-recognition.md
kb/concepts/movement-and-warmup-framework.md
kb/concepts/muscle-memory-through-repetition.md
kb/concepts/positional-control-framework.md
kb/concepts/principles-connect-techniques.md
kb/concepts/submission-framework.md
kb/concepts/techniques-as-recipe-book.md
kb/concepts/uke-and-tori-drilling-roles.md
```

Each page should use frontmatter like:

```md
---
id: basic-bjj-match-strategy
type: concept
title: "Basic BJJ Match Strategy"
status: active
confidence: 0.8
claim_label: fact
source_refs:
- source-kin-bjj-compendium#chunk-...
related_pages: []
domain_tags: [strategy, competition, beginner]
keywords: [match strategy, points strategy, beginner game plan]
summary: Introductory strategy page explaining how positional priorities, scoring awareness, and risk management shape a basic BJJ match approach.
---
```

Use the denser body structure already adopted in the templates.

- [ ] **Step 2: Recreate position, policy, program, and value pages only where current raw files support them**

Target pages include:

```text
kb/position/guard-framework.md
kb/position/knee-on-belly-system.md
kb/position/mount-system.md
kb/position/north-south-system.md
kb/position/passing-framework.md
kb/position/rear-mount-system.md
kb/position/side-control-system.md
kb/position/turtle-system.md
kb/policies/mat-safety-program.md
kb/policies/promotions-model-4a.md
kb/policies/sparring-guidelines.md
kb/programs/future-black-belt-program.md
kb/programs/kids-youth-development-program.md
kb/programs/supplementary-youth-programs.md
kb/values/foundational-youth-values.md
```

Keep only pages the current raw files substantiate. If a page cannot be supported from current source material, do not create it here; capture the gap in Task 6 instead.

- [ ] **Step 3: Use `summary` and `keywords` deliberately on every recreated page**

For each derived page, include:

```md
keywords: [3-6 strong retrieval terms]
summary: One compact sentence that tells an agent what the page covers and why it matters.
```

- [ ] **Step 4: Commit the core knowledge regeneration checkpoint**

```bash
git add kb/concepts kb/position kb/policies kb/programs kb/values
git commit -m "feat: regenerate core kb knowledge pages"
```

### Task 5: Rebuild Class, Procedure, And Lesson Pages

**Files:**
- Create: `kb/class-types/*.md`
- Create: `kb/procedures/*.md`
- Create: `kb/lessons/*.md`

- [ ] **Step 1: Recreate class-type pages from the kids lesson structure and overview material**

Target pages include:

```text
kb/class-types/class-structure-principles.md
kb/class-types/competition-training-session-framework.md
kb/class-types/kids-age-and-duration-guidelines.md
kb/class-types/youth-class-template-60-minutes.md
```

These should be denser than the old versions and preserve operational detail, coaching implications, and structured notes where the raw files support them.

- [ ] **Step 2: Recreate procedure pages with practical detail**

Target pages include:

```text
kb/procedures/announcements-and-student-recognition.md
kb/procedures/drilling-methodology.md
kb/procedures/example-lesson-warmup-option-pattern.md
kb/procedures/example-situational-start-pattern.md
kb/procedures/games-instructional-use.md
kb/procedures/life-skills-chat-framework.md
kb/procedures/roll-call-and-welcome-procedure.md
kb/procedures/technical-lesson-delivery-model.md
kb/procedures/warm-up-philosophy.md
```

Use `Operational Implications` and `Examples or Variants` where the source supports them.

- [ ] **Step 3: Recreate the example-derived lesson pages**

Recreate:

```text
kb/lessons/double-leg-side-control-americana-example-lesson.md
kb/lessons/tots-week-1-mat-rules-base-ready-stance-example.md
```

Include:

```md
## Definition
...

## Detailed Notes
...

## Preserved Example Format

```markdown
... selected preserved lesson structure when useful ...
```
```

Only include preserved format here if it materially helps retrieval and lesson-shape reuse. The source pages remain the canonical full preserved examples.

- [ ] **Step 4: Commit the class/procedure/lesson checkpoint**

```bash
git add kb/class-types kb/procedures kb/lessons
git commit -m "feat: regenerate delivery and lesson-format kb pages"
```

### Task 6: Recreate Open Questions From Current Evidence Gaps

**Files:**
- Create: `kb/open-questions/*.md`

- [ ] **Step 1: Recreate specific open-question pages only where the current raw corpus still leaves real gaps**

Likely pages:

```text
kb/open-questions/scripted-youth-and-adult-example-differentiation.md
kb/open-questions/supplementary-programs-need-full-build-outs.md
kb/open-questions/week-by-week-curriculum-sequence.md
```

Use frontmatter like:

```md
---
id: week-by-week-curriculum-sequence
type: open-question
title: "Week-By-Week Curriculum Sequence"
status: unresolved
confidence: 0.2
source_refs: []
related_pages: []
domain_tags: [gap, curriculum]
keywords: [curriculum sequence, week by week progression, sequencing gap]
summary: Open question tracking the lack of source-authored week-by-week sequencing across the current curriculum material.
---
```

- [ ] **Step 2: Make each open question precise and evidence-based**

The body should state:

```md
# Week-By-Week Curriculum Sequence

## Missing Information
- ...

## Why It Matters
- ...

## Evidence Reviewed
- ...

## Next Evidence Needed
- ...
```

- [ ] **Step 3: Commit the open-question checkpoint**

```bash
git add kb/open-questions
git commit -m "feat: regenerate kb open questions from current source gaps"
```

### Task 7: Rebuild Indexes, Reports, And Manifest

**Files:**
- Verify and refresh: `kb/index.md`
- Verify and refresh: `generated/reports/gap-report.md`
- Verify and refresh: `generated/reports/conflict-report.md`
- Verify and refresh: `generated/reports/improvement-report.md`
- Verify and refresh: `generated/kb-manifest.json`
- Verify and refresh: `.kb-state/link-map.json`

- [ ] **Step 1: Rebuild derived outputs from the regenerated KB**

Run:

```bash
python3 skills/llm-knowledge-base/scripts/rebuild_indexes.py .
```

Expected:

```text
command exits successfully and rewrites index/report/manifest files
```

- [ ] **Step 2: Inspect the manifest for `summary` and `keywords`**

Run:

```bash
python3 - <<'PY'
import json
from pathlib import Path
manifest = json.loads(Path("generated/kb-manifest.json").read_text(encoding="utf-8"))
print(manifest["page_counts"])
sample = next(page for page in manifest["pages"] if page["type"] != "source")
print(sample["id"])
print(sample["keywords"])
print(sample["summary"])
PY
```

Expected:

```text
page counts plus a sample page showing non-empty keywords and summary
```

- [ ] **Step 3: Sanity-check the rebuilt KB index**

Run:

```bash
sed -n '1,120p' kb/index.md
```

Expected:

```text
page counts and typed sections reflecting the regenerated KB tree
```

- [ ] **Step 4: Commit the rebuilt artifacts**

```bash
git add kb/index.md generated/reports generated/kb-manifest.json .kb-state/link-map.json
git commit -m "chore: rebuild kb indexes reports and manifest"
```

### Task 8: Final Verification

**Files:**
- Verify: `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
- Verify: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`
- Verify: `kb/**`
- Verify: `generated/kb-manifest.json`

- [ ] **Step 1: Run the rebuild test suite**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py tests/skills/llm_knowledge_base/test_common.py tests/skills/llm_knowledge_base/test_init_repo.py -q
```

Expected:

```text
all selected tests pass
```

- [ ] **Step 2: Run bytecode verification**

Run:

```bash
python3 -m py_compile skills/llm-knowledge-base/scripts/rebuild_indexes.py
```

Expected:

```text
no output
```

- [ ] **Step 3: Inspect diff scope**

Run:

```bash
git diff --stat HEAD~8..HEAD
```

Expected:

```text
rebuild script, rebuild tests, regenerated kb pages, rebuilt reports, and manifest artifacts only
```

- [ ] **Step 4: Report completion with explicit constraints**

The handoff should explicitly state:

```text
- `kb-old/` was ignored as source material
- example source pages preserve `## Preserved Example Format`
- the KB was regenerated from the seven active raw files only
- manifest records now include `summary` and `keywords`
```
