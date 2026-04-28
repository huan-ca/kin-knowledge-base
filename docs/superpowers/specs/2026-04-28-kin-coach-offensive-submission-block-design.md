# KIN Coach Offensive Submission Block Design

## Context

The coach lesson-plan generator now renders adult and youth lesson files using the preserved example lesson structure as its primary format reference.

The raw adult and youth example lesson files were updated so offensive-cycle lessons now express the finish as a separate section:

- `**Submission: ...**`

The current generator does not reflect that change. It still renders:

- `**Takedown**`
- `**Ground**`
- an inline `Submission / Win Condition` bullet inside the ground block
- `**Situational Options**`

That no longer matches the example format closely enough for offensive cycles.

## Goal

Update adult and youth coach lesson rendering so offensive cycles include a standalone `**Submission: ...**` block while preserving `**Situational Options**` as the live-training portion of class for both offensive and defensive cycles.

## Non-Goals

- Do not change tots lesson formatting.
- Do not remove `Situational Options` from any adult or youth week.
- Do not require a new generator job or output layout.
- Do not change the separate meta grounding or missing-information file structure.

## Chosen Approach

Change only the adult/youth lesson renderer and the supporting tests.

The renderer should branch by cycle:

- offensive cycle:
  - `**Takedown**`
  - `**Ground: ...**`
  - `**Submission: ...**`
  - `**Situational Options**`
- defensive cycle:
  - `**Takedown**`
  - `**Ground: ...**`
  - no standalone submission block
  - `**Situational Options**`

This keeps the live-training section present in both cycle types while matching the updated example format for offensive lessons.

## Rendering Rules

### Offensive Adult and Youth Weeks

The lesson body should render:

- takedown block
- ground block
- standalone submission block
- situational options block

The submission details should move out of the ground block and into the standalone submission block.

The ground block should stay focused on:

- control
- stabilization
- transitions

The submission block should cover:

- named finish
- cue or key detail where practical
- finish-specific coach framing where practical

### Defensive Adult and Youth Weeks

The lesson body should render:

- takedown block
- ground block
- situational options block

Defensive weeks should not force a standalone submission block just for symmetry.

The defensive lesson should remain honest about its emphasis.

### Situational Options

`Situational Options` remains required for both offensive and defensive adult/youth weeks.

This block represents the live-training portion of class and should not be renamed to `Submission / Win Condition`.

For offensive weeks it follows the submission block.

For defensive weeks it follows the ground block directly.

## Data Model Impact

No new output tree or job structure is needed.

The existing week record already carries enough information for this change if the renderer treats:

- `submission`
- `cycle`

as formatting controls.

If the current submission field is too broad, the implementation may tighten its wording generation, but should avoid widening the data model unless needed.

## Testing and Verification

Tests should verify:

- offensive adult/youth lesson files contain a standalone `**Submission:` block
- defensive adult/youth lesson files do not contain that standalone block
- `Situational Options` still appears in both offensive and defensive adult/youth lesson files
- tots outputs are unchanged
- the generator remains deterministic

Manual verification should include:

- one offensive adult lesson
- one defensive adult lesson
- one offensive youth lesson
- one defensive youth lesson

## Files Likely In Scope

- `repo_generators/coach_lesson_plans.py`
- `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`

No broader generator refactor is required for this format change.
