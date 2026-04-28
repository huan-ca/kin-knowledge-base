# KIN Coach Syllabus Table Design

## Context

The coach lesson-plan generator currently emits one syllabus file per program:

- `generated/kin-bjj-coach-lesson-plans/lesson/adult-syllabus.md`
- `generated/kin-bjj-coach-lesson-plans/lesson/youth-syllabus.md`
- `generated/kin-bjj-coach-lesson-plans/lesson/tots-syllabus.md`

Those files currently use a bullet-style summary plus a coach-note footer.

The user wants the syllabus to be rendered as a compact markdown table instead, modeled after the adult example they provided, but simplified to only four columns:

- `Week`
- `Cycle`
- `Theme`
- `Main Goal`

The user also confirmed the same table format should apply to all three syllabus files, not only the adult syllabus.

## Goal

Update syllabus rendering so all generated coach syllabus files use a short intro plus a four-column markdown table:

- `Week`
- `Cycle`
- `Theme`
- `Main Goal`

## Non-Goals

- Do not change weekly lesson-plan structure.
- Do not change meta grounding or missing-information files.
- Do not add extra table columns such as description.
- Do not create separate syllabus formats per program.

## Chosen Approach

Change only the syllabus renderer and its tests.

Each syllabus file should render:

- the existing top-level title
- one short intro sentence
- a markdown table with the four required columns

The current bullet summary and coach-note footer should be removed so the file reads as a clean planning table.

## Table Rules

### Shared Structure

All three syllabus files should use the same table header:

| Week | Cycle | Theme | Main Goal |
| --- | --- | --- | --- |

Rows should be zero-padded by week number where applicable, for example `01`, `02`, `03`.

### Adult and Youth

For adult and youth syllabi:

- `Week` comes from the generated week number
- `Cycle` comes from the generated cycle
- `Theme` comes from the generated week theme
- `Main Goal` comes from the generated teaching goal

### Tots

For tots syllabi:

- use the same four-column table
- `Main Goal` should still come from the generated teaching goal
- no custom tots-only layout should be introduced

This keeps the output consistent even though the tots content remains movement- and game-led.

## Intro Sentence

Each syllabus file should keep a short one-sentence intro above the table.

The sentence should stay coach-facing and compact, for example:

- adult: map the adult weekly sequence to cycle, theme, and main goal
- youth: map the youth weekly sequence to cycle, theme, and main goal
- tots: map the tots weekly sequence to cycle, theme, and main goal

Exact wording may vary slightly by program name, but the structure should remain short and consistent.

## Testing and Verification

Tests should verify:

- adult syllabus renders a markdown table with the four required columns
- youth syllabus renders the same table format
- tots syllabus renders the same table format
- the old coach-note footer is no longer present
- week rows are zero-padded

Manual verification should include opening all three generated syllabus files and confirming they are easy to scan as tables.

## Files Likely In Scope

- `repo_generators/coach_lesson_plans.py`
- `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`

No broader generator refactor is required for this change.
