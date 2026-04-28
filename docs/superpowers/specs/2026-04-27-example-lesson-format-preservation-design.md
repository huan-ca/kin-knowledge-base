# Example Lesson Format Preservation Design

## Context

The newly added raw example lesson files are format-carrying artifacts:

- `raw/example_scripted_lesson_plan_adult.md`
- `raw/example_scripted_lesson_plan_youth.md`
- `raw/example_scripted_lesson_plan_tots.md`

The important information in these files is not mainly the specific technique pairing inside the sample week. The important information is the authored markdown structure itself:

- section ordering
- heading style
- fenced markdown usage
- block naming such as opening script, warm-up options, lesson, and closing script
- the shape of how a scripted example is presented

The prior ingestion flattened these sources into summary claims and lesson pages that over-emphasized the example content. That loses the actual format evidence the user wants preserved.

## Goal

Preserve the full example markdown format inside `kb/` so downstream work can recover the example structure faithfully.

## Non-Goals

- Do not invent a new canonical domain type.
- Do not treat the sample technical sequence itself as more authoritative than the surrounding format.
- Do not rewrite `raw/`.

## Chosen Approach

Preserve full example structure on both the `source` pages and the derived `lesson` pages.

### Source Pages

Each `source` page for the three example lesson files should:

- reflect the new `example_*` raw filenames
- preserve provenance and extracted claims
- add a dedicated `## Preserved Example Format` section
- include the example body in a fenced `markdown` block

The fenced block should preserve the authored format as closely as practical.

### Derived Lesson Pages

Derived `lesson` pages created from these examples should also preserve the example structure instead of collapsing it into normal KB prose.

Each such lesson page should:

- remain clearly marked as an example, not a canonical approved lesson
- include a short explanation of what the example demonstrates
- include a dedicated preserved-format section with the fenced markdown block
- keep any extracted details focused on structural observations rather than over-committing to the exact sample content

## Naming

The KB source-page naming should follow the renamed raw files:

- `source-example-scripted-lesson-plan-adult`
- `source-example-scripted-lesson-plan-youth`
- `source-example-scripted-lesson-plan-tots`

The file names under `kb/sources/` should align with those raw filenames.

Derived lesson pages should also use names that communicate example status rather than canonical lesson status.

## Extraction Rules

For these example lesson sources:

- treat formatting as first-class evidence
- preserve markdown structure verbatim where practical
- keep summaries short
- keep extracted claims format-oriented
- avoid turning one example’s sample theme into a broad curriculum truth

Good extracted claims include:

- the example uses an opening script section
- the example separates warm-up options from the main lesson body
- the example uses named technical sub-blocks
- the example ends with a closing script or situational options

Weak extracted claims include:

- implying the exact sample sequence is the standard adult or youth curriculum
- implying the sample week is canonical gym programming

## Open Question Handling

The youth and adult example duplication issue should stay explicit.

If the youth example still substantially mirrors the adult example, retain an `open-question` page noting that the format may be intentional while the audience-specific content may still need clarification.

## Rebuild Behavior

After updating the KB pages:

- rebuild indexes and reports
- verify the new source and lesson pages appear in `kb/index.md`
- ensure the preserved-format example pages are discoverable through normal KB navigation

## Verification

- confirm the three renamed example raw files are represented in `kb/sources/`
- confirm each of those source pages includes a fenced `markdown` block
- confirm the derived example lesson pages also include fenced `markdown` blocks
- run `python3 skills/llm-knowledge-base/scripts/rebuild_indexes.py .`
