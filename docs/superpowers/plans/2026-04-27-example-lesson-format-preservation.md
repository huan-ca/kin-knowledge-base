# Example Lesson Format Preservation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the authored markdown structure of the `example_*` scripted lesson sources in both `kb/sources/` and the derived KB lesson pages.

**Architecture:** Treat the renamed `raw/example_*` files as format-carrying source artifacts first and content examples second. Update the source pages to embed the example body in fenced `markdown` blocks, update the derived lesson pages to preserve the same example block with explicit “example” framing, then rebuild KB indexes and reports against the current repo state.

**Tech Stack:** Markdown KB pages, repo-local LLM knowledge base conventions, `python3 skills/llm-knowledge-base/scripts/rebuild_indexes.py`

---

### Task 1: Replace the Source Pages With Format-Preserving Example Sources

**Files:**
- Delete: `kb/sources/scripted-lesson-plan-adult.md`
- Delete: `kb/sources/scripted-lesson-plan-youth.md`
- Delete: `kb/sources/scripted-lesson-plan-tots.md`
- Create: `kb/sources/example-scripted-lesson-plan-adult.md`
- Create: `kb/sources/example-scripted-lesson-plan-youth.md`
- Create: `kb/sources/example-scripted-lesson-plan-tots.md`

- [ ] **Step 1: Write the failing content expectation**

Use these target sections for all three replacement source pages:

```md
## Summary
This source is an example scripted lesson-plan artifact where the markdown structure itself is evidence that should be preserved for downstream retrieval and generation.

## Preserved Example Format

```markdown
[full example body copied from raw/example_*.md]
```
```

- [ ] **Step 2: Verify the current source pages do not preserve the example markdown**

Run: `rg -n "Preserved Example Format|```markdown" kb/sources/scripted-lesson-plan-adult.md kb/sources/scripted-lesson-plan-youth.md kb/sources/scripted-lesson-plan-tots.md`

Expected: no `Preserved Example Format` section and no preserved fenced markdown block in the existing source pages.

- [ ] **Step 3: Replace the old source pages with renamed example-source pages**

Create pages using this shape, with source-specific ids, file names, hashes, and preserved blocks:

```md
---
id: source-example-scripted-lesson-plan-adult
type: source
title: "example_scripted_lesson_plan_adult.md"
status: active
confidence: 1.0
source_refs: []
related_pages: []
ingestion_batch: batch-20260428T044832Z
---
# example_scripted_lesson_plan_adult.md

## Artifact
- Path: `raw/example_scripted_lesson_plan_adult.md`
- Hash: `[current sha256 from .kb-state/raw-manifest.json]`

## Summary
This source is an example scripted adult lesson-plan artifact. The authored markdown format is preserved because the format itself is part of the source evidence.

## Extracted Claims
- The source presents a week example as a formatted scripted lesson artifact rather than a bare list of techniques. (`chunk-001`)
- The source uses distinct sections for week metadata, opening script, warm-up options, technical lesson blocks, and situational training. (`chunk-002`)

## Preserved Example Format

```markdown
[copy the full preserved example body exactly as authored in raw/example_scripted_lesson_plan_adult.md]
```

## Open Questions
- The source is an example format artifact, so it does not by itself establish a canonical gym-wide adult lesson library.
```

Apply the same pattern to youth and tots with:
- `source-example-scripted-lesson-plan-youth`
- `source-example-scripted-lesson-plan-tots`

- [ ] **Step 4: Verify the replacement source pages contain preserved markdown blocks**

Run: `rg -n "source-example-scripted-lesson-plan|Preserved Example Format|```markdown" kb/sources/example-scripted-lesson-plan-adult.md kb/sources/example-scripted-lesson-plan-youth.md kb/sources/example-scripted-lesson-plan-tots.md`

Expected: each file contains the renamed source id and a `## Preserved Example Format` section followed by a fenced `markdown` block.

- [ ] **Step 5: Commit**

```bash
git add kb/sources/example-scripted-lesson-plan-adult.md kb/sources/example-scripted-lesson-plan-youth.md kb/sources/example-scripted-lesson-plan-tots.md kb/sources/scripted-lesson-plan-adult.md kb/sources/scripted-lesson-plan-youth.md kb/sources/scripted-lesson-plan-tots.md
git commit -m "feat: preserve example lesson markdown in source pages"
```

### Task 2: Reframe the Derived Lesson Pages as Example-Format Pages

**Files:**
- Modify: `kb/lessons/double-leg-side-control-americana-example-lesson.md`
- Modify: `kb/lessons/tots-week-1-mat-rules-base-ready-stance-example.md`
- Modify: `kb/open-questions/scripted-youth-and-adult-example-differentiation.md`

- [ ] **Step 1: Write the failing content expectation**

Both lesson pages should include a preserved-format section and explicit example framing:

```md
## Example Status
- This page preserves an example lesson format artifact and should not be treated as a canonical approved lesson.

## Preserved Example Format

```markdown
[full example block]
```
```

- [ ] **Step 2: Verify the current lesson pages do not preserve the example markdown**

Run: `rg -n "Example Status|Preserved Example Format|```markdown" kb/lessons/double-leg-side-control-americana-example-lesson.md kb/lessons/tots-week-1-mat-rules-base-ready-stance-example.md`

Expected: the current lesson pages do not yet contain preserved example-format sections.

- [ ] **Step 3: Update the lesson pages to preserve the example markdown**

Use this structure for the adult/youth shared example page:

```md
## Definition
This page records a reusable example lesson format artifact built around a connected takedown-to-control-to-finish sequence.

## Example Status
- This is an example lesson-format page, not a canonical approved curriculum lesson.

## Structural Observations
- The example begins with week metadata.
- The example includes an opening script.
- The example separates warm-up options from the lesson block.
- The example ends with situational options rather than only static drilling notes.

## Preserved Example Format

```markdown
[full preserved block from the adult example source]
```

## Gaps
- The current youth counterpart may still need audience-specific differentiation.
```

Use this structure for the tots page:

```md
## Definition
This page records a tots example lesson-format artifact for a short foundation-cycle class.

## Example Status
- This is an example lesson-format page, not a canonical approved curriculum lesson.

## Structural Observations
- The example uses a simple lesson script rather than multi-option technical blocks.
- The example keeps movement, game, and intro-grappling sections distinct.

## Preserved Example Format

```markdown
[full preserved block from the tots example source]
```
```

Update the open question so it references the renamed example source ids:

```md
source_refs:
- source-example-scripted-lesson-plan-adult#chunk-001
- source-example-scripted-lesson-plan-youth#chunk-001
- source-example-scripted-lesson-plan-youth#chunk-002
```

- [ ] **Step 4: Verify the derived pages preserve the example blocks**

Run: `rg -n "Example Status|Preserved Example Format|```markdown|source-example-scripted-lesson-plan" kb/lessons/double-leg-side-control-americana-example-lesson.md kb/lessons/tots-week-1-mat-rules-base-ready-stance-example.md kb/open-questions/scripted-youth-and-adult-example-differentiation.md`

Expected: the lesson pages now include preserved-format blocks and the open question references the renamed example source ids.

- [ ] **Step 5: Commit**

```bash
git add kb/lessons/double-leg-side-control-americana-example-lesson.md kb/lessons/tots-week-1-mat-rules-base-ready-stance-example.md kb/open-questions/scripted-youth-and-adult-example-differentiation.md
git commit -m "feat: preserve example lesson markdown in derived pages"
```

### Task 3: Refresh KB State and Verify Discoverability

**Files:**
- Modify: `kb/index.md`
- Modify: `generated/reports/gap-report.md`
- Modify: `generated/reports/improvement-report.md`
- Modify: `.kb-state/link-map.json`
- Modify: `.kb-state/raw-manifest.json`
- Modify: `.kb-state/ingestion-plan.json`

- [ ] **Step 1: Verify the renamed raw files are present in manifest state**

Run: `rg -n "example_scripted_lesson_plan_(adult|youth|tots)\\.md" .kb-state/raw-manifest.json .kb-state/ingestion-plan.json`

Expected: the manifest and ingestion plan reflect the renamed `example_*` raw files.

- [ ] **Step 2: Rebuild indexes and reports**

Run: `python3 skills/llm-knowledge-base/scripts/rebuild_indexes.py .`

Expected: exit `0` and refreshed KB/report outputs.

- [ ] **Step 3: Verify discoverability**

Run: `rg -n "example_scripted_lesson_plan_adult|example_scripted_lesson_plan_youth|example_scripted_lesson_plan_tots|Double Leg to Side Control to Americana Example Lesson|Tots Week 1 Mat Rules, Base, And Ready Stance Example" kb/index.md generated/reports/gap-report.md generated/reports/improvement-report.md`

Expected: the rebuilt index lists the renamed source pages and the example lesson pages.

- [ ] **Step 4: Commit**

```bash
git add kb/index.md generated/reports/gap-report.md generated/reports/improvement-report.md .kb-state/link-map.json .kb-state/raw-manifest.json .kb-state/ingestion-plan.json
git commit -m "chore: rebuild kb outputs for preserved example lesson formats"
```

## Self-Review

### Spec Coverage
- Source pages preserve fenced markdown blocks: covered by Task 1.
- Derived lesson pages preserve fenced markdown blocks: covered by Task 2.
- Example status is explicit and non-canonical: covered by Task 2.
- Rebuild and discoverability checks: covered by Task 3.

### Placeholder Scan
- No `TBD`, `TODO`, or “similar to previous task” placeholders remain.
- Exact files, commands, and expected outcomes are included for each task.

### Type Consistency
- Source ids use `source-example-scripted-lesson-plan-*` consistently.
- Derived pages remain `type: lesson`.
- The clarification page remains `type: open-question`.
