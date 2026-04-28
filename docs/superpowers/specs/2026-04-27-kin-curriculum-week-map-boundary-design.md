# KIN Curriculum Week-Map Boundary Design

## Context

The repository currently contains three synthesized calendar pages under `kb/curriculum/`:

- `adult-24-week-theme-map.md`
- `youth-24-week-theme-map.md`
- `tots-12-week-theme-map.md`

Those pages behave like generated curriculum candidates, not normalized knowledge. They were produced by a previous version of the workflow and then published back into `kb/`. That breaks the repo contract:

- `raw/` is human evidence
- `kb/` is normalized knowledge/frameworks
- `generated/` is reproducible output

The user wants the week-by-week curriculum maps removed from `kb/`, regenerated as candidate artifacts under `generated/`, and then used as the deterministic source for downstream curriculum files. If the generated week maps are later approved, promotion back into `raw/` should be a separate manual step.

## Goals

- Remove only the three calendar week-map pages from `kb/curriculum/`.
- Keep framework and concept pages in `kb/` intact.
- Rebuild KB indexes and reports so they stop referencing the removed week-map pages.
- Generate replacement candidate week maps under `generated/kin-bjj-weekly-curriculum/week-maps/`.
- Deterministically generate curriculum outputs from those generated week maps.
- Keep the promotion path manual: no automatic write-back from generated artifacts into `kb/` or `raw/`.
- Surface gaps when the framework KB is insufficient to support a confident week sequence.

## Non-Goals

- Do not change `raw/`.
- Do not automatically ingest generated week maps back into `kb/`.
- Do not introduce fallback reads from the removed `kb/curriculum/*-theme-map.md` files.
- Do not redesign the published output set beyond changing the source boundary.

## Chosen Approach

Use a two-stage generation flow inside the existing `kin-bjj-weekly-curriculum` job.

### Stage 1: Candidate Week-Map Synthesis

Stage 1 reads only approved framework knowledge from `kb/` plus existing job notes/examples and writes candidate week maps to:

- `generated/kin-bjj-weekly-curriculum/week-maps/adult-24-week-theme-map.md`
- `generated/kin-bjj-weekly-curriculum/week-maps/youth-24-week-theme-map.md`
- `generated/kin-bjj-weekly-curriculum/week-maps/tots-12-week-theme-map.md`

These files are generated artifacts, not KB pages.

### Stage 2: Deterministic Curriculum Rendering

Stage 2 reads only the generated week maps from `generated/kin-bjj-weekly-curriculum/week-maps/` and deterministically renders:

- `curriculum`
- `quick-outline`
- `coach-guide`
- `fully-scripted-session`
- program syllabi

Stage 2 must fail if week-map artifacts are missing or malformed. It must not fall back to `kb/curriculum/*-theme-map.md`.

## Why This Approach

This preserves the intended repository boundary:

- `kb/` remains the normalized framework layer
- `generated/` contains synthetic curriculum candidates and downstream artifacts
- manual human review stays between generation and any later source promotion

It also minimizes churn in the current deterministic renderer because the renderer can continue consuming structured week-map data rather than re-deriving each lesson file directly from sparse framework pages.

## Week-Map Artifact Contract

Each generated week-map file should be a self-contained candidate artifact with frontmatter plus a fenced JSON payload.

### Frontmatter

Required fields:

- `id`
- `type`
- `title`
- `status`
- `source_kb_pages`
- `generation_notes`
- `warnings`
- `confidence`

Suggested `type` value:

- `generated-curriculum-candidate`

### Body

The markdown body should contain:

- a short human-readable summary
- one fenced `json` block containing a top-level `weeks` array

### Week Entry Shape

Each week entry should preserve the current deterministic renderer contract as much as possible:

- `week`
- `cycle`
- `theme`
- `focus`
- `teaching_goal`
- `takedown`
- `ground`
- `submission`
- `level_1`
- `level_2`
- optional `coach_notes`
- optional `gaps`

This keeps Stage 2 mostly compatible with the current `repo_generators/curriculum.py` rendering path.

## KB Inputs And Gap Handling

Stage 1 should synthesize week maps from KB framework pages, not from `raw/`.

Relevant KB support already exists for:

- weekly design rules
- offensive and defensive cycle expectations
- takedown families
- groundwork families
- youth submission safety constraints
- adult leg-lock placement guidance

The KB is still incomplete for a fully authoritative calendar. Known gaps include:

- exact week-by-week position sequencing
- precise takedown family ordering per program
- exact submission pairings per week
- a complete youth age or belt legality matrix
- exact adult leg-lock lesson sequencing in the final cycle

Stage 1 must not hide these gaps. It should:

- fail if essential framework pages are missing
- emit file-level warnings when sequencing decisions are inferred
- attach week-level `gaps` when a specific week depends on a weak inference
- lower file confidence when the calendar is mostly synthesized from framework constraints rather than explicit source-authored sequence material

## Job And Generator Changes

The `kin-bjj-weekly-curriculum` job should be updated so it no longer lists the removed KB week-map pages as direct inputs.

Instead:

- job inputs continue to include KB/framework references needed by Stage 1
- Stage 1 writes generated week maps under `generated/.../week-maps/`
- Stage 2 consumes those generated week maps only

The generator implementation should be refactored so the current `load_program_data()` logic no longer points at `kb/curriculum/*-theme-map.md`. It should instead load the generated candidate artifacts from the job output tree.

## Migration Plan

1. Delete:
   - `kb/curriculum/adult-24-week-theme-map.md`
   - `kb/curriculum/youth-24-week-theme-map.md`
   - `kb/curriculum/tots-12-week-theme-map.md`
2. Rebuild KB indexes and reports so they stop linking to those pages.
3. Update job configuration and generator code for the new two-stage flow.
4. Generate new candidate week maps under `generated/kin-bjj-weekly-curriculum/week-maps/`.
5. Generate downstream curriculum files deterministically from those candidate week maps.

## Failure Behavior

- Stage 1 fails if required KB framework pages are missing.
- Stage 1 succeeds with warnings if framework support is partial but sufficient for a best-effort candidate calendar.
- Stage 2 fails fast if generated week maps are missing, malformed, or incomplete.
- No component may silently fall back to the deleted KB week-map pages.

## Verification Plan

- Add tests for Stage 1 week-map artifact shape.
- Add tests for warnings and gap emission when sequencing is inferred.
- Add tests proving Stage 2 reads `generated/.../week-maps/` rather than `kb/...theme-map.md`.
- Add tests for index rebuild after the KB week-map deletion.
- Run:
  - `python3 skills/llm-knowledge-base/scripts/rebuild_indexes.py .`
  - `python3 skills/llm-knowledge-base/scripts/run_generation.py . --job-name kin-bjj-weekly-curriculum`

## Risks

- The remaining KB framework may still be too thin for a high-quality first-pass week calendar. If so, the right fix is to enrich the framework KB or manually add approved source material to `raw/`, not to move generated guesses back into `kb/`.
- Existing tests and reports may assume the week-map pages still exist in `kb/`; those assumptions need to be updated explicitly.
- The current generator was built around a single-stage model, so the refactor should keep Stage 1 and Stage 2 interfaces narrow to avoid unnecessary breakage.

## Resulting Repository Contract

After this change, the intended lifecycle becomes:

`raw evidence -> kb frameworks -> generated candidate week maps -> generated curriculum files`

Any later promotion of a generated curriculum artifact back into source material remains a deliberate human action:

`generated candidate -> human review -> manual add to raw/ -> later ingestion into kb/`
