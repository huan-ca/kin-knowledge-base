# Coach Lesson Plan Regeneration Design

## Goal

Regenerate the coach lesson plan output from the denser active `kb/` so the lesson files are less terse, more coach-useful, and still explicitly separated from provenance-heavy review material.

This change should also archive the current generated output tree by renaming `generated/kin-bjj-coach-lesson-plans/` to `generated/kin-bjj-coach-lesson-plans-old/` before writing the new output tree.

## Scope

This design applies only to the generated output tree and the coach lesson plan generator behavior.

It does not rename or replace the existing job definition under `jobs/kin-bjj-coach-lesson-plans/`.

It does not change the job name.

It does not change the broad program contract:

- adult: 24 weeks
- youth: 24 weeks
- tots: 12 weeks

It does not pretend the KB contains a fully source-authored week-by-week curriculum sequence where it does not.

## Output Boundary

Before regeneration:

- if `generated/kin-bjj-coach-lesson-plans/` exists, rename it to `generated/kin-bjj-coach-lesson-plans-old/`
- if `generated/kin-bjj-coach-lesson-plans-old/` already exists, replace it deterministically so the archive does not accumulate nested stale outputs

After regeneration:

- write fresh outputs to `generated/kin-bjj-coach-lesson-plans/`

The lesson tree remains:

- `generated/kin-bjj-coach-lesson-plans/lesson/adult/...`
- `generated/kin-bjj-coach-lesson-plans/lesson/youth/...`
- `generated/kin-bjj-coach-lesson-plans/lesson/tots/...`
- syllabus files under `generated/kin-bjj-coach-lesson-plans/lesson/`

The meta tree changes to:

- weekly grounding files:
  - `generated/kin-bjj-coach-lesson-plans/meta/adult/week-XX-kb-grounding.md`
  - `generated/kin-bjj-coach-lesson-plans/meta/youth/week-XX-kb-grounding.md`
  - `generated/kin-bjj-coach-lesson-plans/meta/tots/week-XX-kb-grounding.md`
- one consolidated missing-info file per program:
  - `generated/kin-bjj-coach-lesson-plans/meta/adult/missing-info.md`
  - `generated/kin-bjj-coach-lesson-plans/meta/youth/missing-info.md`
  - `generated/kin-bjj-coach-lesson-plans/meta/tots/missing-info.md`

The repeated per-week `week-XX-missing-info.md` files are removed.

## Lesson Content Strategy

The existing generator is too terse because it relies on a narrow heuristic week schema and only uses the KB as a formatting prerequisite.

The new generator should still keep deterministic heuristic sequencing, but it should use the richer KB page bodies to expand the generated coach lesson plans.

The generator should pull concise, reusable coaching detail from the KB, including when available:

- definition-level framing
- detailed notes
- operational implications
- examples or variants
- constraints or safety notes

This detail should be mapped into coach-facing lesson sections without exposing raw provenance fields inside the lesson files.

The lesson files should remain list-heavy and coach-readable.

## Program-Specific KB Use

Adult and youth lesson generation should draw from a fixed deterministic set of KB sources such as:

- example lesson-format pages
- class-structure pages
- lesson-delivery and warm-up procedure pages
- escape, guard, control, passing, and submission framework pages
- youth-values and youth-development pages for youth framing

Tots generation should draw from:

- the tots example lesson-format page
- youth/class-structure pages where relevant
- movement/warm-up framework pages
- safety and behavior framing pages where relevant

This is not freeform retrieval. It is deterministic KB selection plus heuristic synthesis.

## Lesson File Expectations

Lesson files under `lesson/` remain final coach documents.

They should not include raw manifest or provenance-style metadata such as:

- claim labels
- source refs
- confidence scores
- explicit grounded vs inferred markers

If uncertainty needs to surface in a lesson file, it must be reframed as coach-useful caution language.

The new denser lesson files should improve:

- opening script specificity
- warm-up framing
- technical block detail
- coach notes
- safety cues
- closing emphasis

They should remain concise enough to run from live, but no longer read like skeletal placeholders.

## Meta File Expectations

Weekly `week-XX-kb-grounding.md` files remain the detailed provenance layer for each week.

Each program-level `missing-info.md` should:

- list repeated program-wide gaps once
- list only material week-specific human decisions
- avoid boilerplate duplication across weeks
- remain easy for a human reviewer to fill or annotate

## Determinism and Honesty

The generator must remain deterministic across runs for the same repo state.

The output must remain explicit that:

- week sequencing is heuristic
- detailed week content is partly KB-grounded and partly inferred
- unsupported decisions belong in `meta/`, not hidden in coach files

## Verification

Implementation should verify:

- coach lesson plan tests pass
- generation runner tests still pass
- the job regenerates successfully
- the old output folder is archived as designed
- program-level `missing-info.md` files replace the repeated per-week versions
