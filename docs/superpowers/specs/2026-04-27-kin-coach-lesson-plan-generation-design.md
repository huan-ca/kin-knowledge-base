# KIN Coach Lesson Plan Generation Design

## Context

The repository now has:

- preserved example-format KB pages for adult, youth, and tots scripted lessons
- general source material about KIN BJJ lesson structure and program intent
- a separate weekly curriculum generator whose outputs do not match the example format the coaches actually need

The current `kin-bjj-weekly-curriculum` job is not a good base for this work:

- its existing job spec still points at removed `kb/curriculum/*-theme-map.md` inputs
- its rendered files are split into curriculum, outline, coach-guide, and scripted-session variants instead of one final coach-facing lesson document
- its markdown shape does not preserve the example lesson format as the primary artifact

The user wants a separate generation job that produces coach-ready lesson plans in the example format, uses lists rather than large prose blocks, and keeps provenance and gap reporting outside the coach-facing files.

## Goal

Create a new job-scoped generator that produces:

- coach-facing weekly lesson-plan files for `adult`, `youth`, and `tots`
- one syllabus file per program
- one KB-grounding report per week
- one missing-information file per week when the KB does not support a confident plan

The new outputs must preserve the example lesson shape as the primary rendering format, while honestly marking where weekly content is inferred rather than directly KB-grounded.

## Non-Goals

- Do not retrofit the existing `kin-bjj-weekly-curriculum` job to this format.
- Do not edit `raw/`.
- Do not treat generated week sequencing as source-authored fact.
- Do not put raw provenance fields or audit-style metadata into coach-facing lesson files.
- Do not require a perfect semantic parser for freeform source prose.

## Chosen Approach

Build a new dedicated generation job that synthesizes weekly coach lesson plans from KB evidence plus deterministic program rules.

The job should:

- read from `kb/` and job-local examples only
- synthesize a deterministic weekly teaching sequence for each program
- render polished coach documents under `lesson/`
- render explicit provenance and gap files under `meta/`
- preserve the example markdown shape on the coach-facing files

This keeps the output format aligned with the example lessons while preserving honest provenance boundaries in separate meta files.

## Output Layout

The new job should write into a separate generated tree:

- `generated/kin-bjj-coach-lesson-plans/lesson/adult-syllabus.md`
- `generated/kin-bjj-coach-lesson-plans/lesson/youth-syllabus.md`
- `generated/kin-bjj-coach-lesson-plans/lesson/tots-syllabus.md`
- `generated/kin-bjj-coach-lesson-plans/lesson/adult/week-01-lesson-plan.md`
- `generated/kin-bjj-coach-lesson-plans/lesson/youth/week-01-lesson-plan.md`
- `generated/kin-bjj-coach-lesson-plans/lesson/tots/week-01-lesson-plan.md`
- `generated/kin-bjj-coach-lesson-plans/meta/adult/week-01-kb-grounding.md`
- `generated/kin-bjj-coach-lesson-plans/meta/adult/week-01-missing-info.md`
- parallel `meta/` files for `youth` and `tots`

Conventions:

- all week filenames are zero-padded
- `lesson/` contains only coach-facing files
- `meta/` contains grounding and missing-information files
- the job should reset its own generated output tree deterministically on each run

## Input Model

The generator should use only stable inputs under `kb/` plus job-local examples:

- source pages about overall program structure and lesson shape
- preserved example lesson pages for adult, youth, and tots
- concept and procedure pages derived from those sources
- job-local example documents under `jobs/<job-name>/examples/` when needed for rendering conventions

The generator should not depend on the existing weekly curriculum job’s old `job.yaml` inputs or assume `kb/curriculum/` pages exist.

Instead, it should build weekly plans from:

- current KB evidence about class structure and teaching format
- explicit program rules in the new job spec
- deterministic heuristic sequencing rules

## Program Rules

### Adult

- 24 weeks
- same broad weekly structure as youth
- includes lower-body/leg-lock content in the adult-only weeks
- should still keep weekly plans safe and coach-usable rather than competition-specialist

### Youth

- 24 weeks
- same broad weekly structure as adult
- uses youth framing
- uses self-defence emphasis where adult uses leg-lock emphasis
- should stay age-appropriate and coach-friendly

### Tots

- 12 weeks
- movement-led and game-heavy
- lighter technical density
- stronger emphasis on attention, transitions, balance, athletic development, and fun
- should not read like a stripped-down adult technique plan

## Weekly Synthesis Model

The generator should synthesize one structured weekly plan record per program/week before rendering markdown.

Each weekly record should include:

- week number
- program
- theme title
- teaching goal
- warm-up focus
- main teaching blocks
- coach notes
- game or situational work
- closing focus
- grounding summary
- inferred content summary
- missing-information prompts when needed

This intermediate structure may be held in memory or emitted as transient JSON within the generated job tree, but the key boundary is that rendering should not directly improvise each markdown file independently.

## Lesson File Format

Each `lesson/.../week-XX-lesson-plan.md` file should be a final document that a coach can read and use directly.

It should preserve the example lesson style:

- heading-led structure
- list-heavy content
- concise coach-useful wording
- optional short scripts where helpful
- explicit blocks such as opening, warm-up, lesson, situational/game work, and closing

It should not include raw provenance fields such as:

- `source_refs`
- `claim_label`
- `confidence`
- `kb_grounded`
- `missing_info`

If uncertainty needs to appear in the lesson file, it must be reframed as a coach-useful note, for example a safety note, intensity note, or provisional-teaching note.

## Syllabus File Format

Each program syllabus file should sit at the root of `lesson/` and provide a compact season view for coaches.

Each syllabus should include:

- program summary
- total weeks
- broad phase grouping if used
- one line per week with theme and goal
- special notes for adult leg-lock weeks, youth self-defence weeks, or tots movement/game emphasis

The syllabus is a coach planning artifact, not an audit file.

## Grounding Reports

Each `meta/<program>/week-XX-kb-grounding.md` file should explicitly distinguish:

- what was directly supported by KB pages
- what was inferred from deterministic synthesis rules
- what was adapted from the example format
- what remains weakly supported

These files should be easy for a human reviewer to scan. Prefer short bullets and file references over long narrative.

## Missing-Information Files

Each `meta/<program>/week-XX-missing-info.md` file should only be created when a meaningful human decision is still needed.

These files should be fill-in-ready, with short prompts and clear answer slots, for example:

- preferred self-defence scenario emphasis
- allowed leg-lock depth for this audience
- class length assumptions
- competition vs fundamentals emphasis

If a week has no material missing-information burden, the generator may omit the file entirely or emit a compact “no additional input required” file. The implementation should choose one behavior and apply it consistently.

## Provenance and Honesty Rules

The job must not present synthesized weekly content as if it were directly authored in the source material.

Rules:

- treat example lesson pages primarily as format evidence and secondarily as content evidence
- separate direct KB support from inferred BJJ knowledge
- use conservative confidence language in meta files
- lower confidence when a week requires substantial synthesis
- emit missing-information files rather than pretending the KB answered a decision it did not answer

## Determinism

The new job should be deterministic for the same repo state.

That means:

- stable output paths
- stable week ordering
- stable filename ordering
- deterministic sequencing rules
- deterministic wording templates where practical

The generator should not produce materially different weekly plans across runs without KB or job-input changes.

## Failure Handling

If required KB evidence is missing, the job should fail usefully rather than silently degrade.

Expected cases:

- if example-format KB pages are missing, fail with a message that the coach-format source examples are required
- if program-count rules are missing from the job spec, fail with a configuration error
- if a week cannot be responsibly rendered, emit the meta missing-information file and use a constrained provisional lesson plan instead of inventing certainty

## Testing and Verification

The implementation should add focused tests for:

- output tree reset behavior
- adult, youth, and tots syllabus generation
- coach-facing lesson file paths and naming
- list-heavy example-style lesson rendering
- separation of coach lesson files from provenance-heavy meta files
- KB-grounding report generation
- missing-information file generation for under-supported weeks
- deterministic output for repeated runs

Manual verification should include:

- inspect one adult, one youth, and one tots lesson file for format fidelity
- inspect one KB-grounding report and one missing-information file
- confirm the lesson files read like final coach documents rather than audits

## Files Likely In Scope

Primary implementation files are likely to include:

- a new generator module under `repo_generators/`
- a new job spec under `jobs/`
- generation tests under `tests/skills/llm_knowledge_base/`
- optional example files under `jobs/<job-name>/examples/`

The exact filenames can be finalized in the implementation plan.
