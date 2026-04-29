# Raw-Only KB Regeneration Design

## Summary

Regenerate the `kb/` tree from the current `raw/` corpus only, ignoring `kb-old/` as source material. The rebuild should create dense source-backed KB pages, preserve as much supported source detail as practical, retain the authored example lesson markdown format for the `example_*` raw files, and rebuild the machine-readable manifest with `summary` and `keywords` fields so lookup agents can scan for relevant pages quickly.

## Problem

The current `kb/` tree in the main worktree is largely deleted, while the source material in `raw/` is still present. The repository does not have a single script that can fully reconstruct all KB pages from raw files automatically. A fresh manual ingestion pass is needed.

The prior KB also suffered from a terseness problem. A simple restore of old page shapes would preserve coverage but continue to produce weak downstream generation.

## Goals

- Rebuild `kb/` from the current `raw/` files only
- Preserve provenance conservatively and avoid importing unsupported detail
- Create denser article pages that retain more useful source information
- Preserve the markdown example structure in the example source pages
- Rebuild the JSON manifest with retrieval-friendly `summary` and `keywords`
- Rebuild KB indexes and reports after the regeneration pass

## Non-Goals

- Using `kb-old/` as source content
- Treating deleted KB pages as authoritative just because they existed before
- Reconstructing unsupported curriculum sequencing from memory
- Editing `raw/`

## Source Scope

The regeneration pass should use only these current raw files:

- `raw/KIN BJJ Compendium.md`
- `raw/KIN BJJ kids lesson plan structure.md`
- `raw/high level overview.md`
- `raw/the_four_layers_of_bjj_skills_development.md`
- `raw/example_scripted_lesson_plan_adult.md`
- `raw/example_scripted_lesson_plan_youth.md`
- `raw/example_scripted_lesson_plan_tots.md`

Removed PDF files and renamed older scripted lesson files should not be treated as active source inputs.

## Design

### 1. Regeneration Boundary

Treat this as a fresh normalization pass from `raw/` into `kb/`.

Outputs should include:

- source pages under `kb/sources/`
- derived knowledge pages across the configured taxonomy
- open-question pages where evidence is incomplete, ambiguous, or still missing
- rebuilt `kb/index.md`
- rebuilt reports under `generated/reports/`
- rebuilt JSON manifest

The pass should ignore `kb-old/` entirely as a source of facts or phrasing.

### 2. Dense Page Standard

Derived pages should not collapse into thin summaries.

They should preserve:

- important distinctions
- structural explanations
- practical implications
- examples or variants when source-supported
- constraints or cautions when source-supported
- clear gap statements where evidence stops

This should follow the denser page contract already adopted in the KB templates and guidance, so regenerated pages become stronger retrieval units for downstream generation.

### 3. Source Pages

Create one source page per raw artifact.

Source pages should:

- preserve a concise source summary
- capture major extracted claims and section-level detail
- carry explicit provenance and confidence
- link to relevant derived pages where practical

The source pages should remain evidence-first, not broad editorial rewrites.

### 4. Example Files And Preserved Example Format

The example raw files require special handling:

- `raw/example_scripted_lesson_plan_adult.md`
- `raw/example_scripted_lesson_plan_youth.md`
- `raw/example_scripted_lesson_plan_tots.md`

For these files, the KB source pages must include:

- `## Preserved Example Format`

That section should retain the authored example body as a fenced markdown block, preserving the instructional format itself as knowledge.

This is important because the markdown structure is part of what downstream lesson generators need to recover.

Derived pages may extract reusable lesson-format ideas, but the preserved example block remains the canonical structured reference.

### 5. Derived Page Coverage

The regeneration pass should rebuild as much supported coverage as practical from the raw corpus.

Likely page families include:

- `concept`
- `procedure`
- `lesson`
- `class-type`
- `program`
- `policy`
- `position`
- `value`
- `open-question`

Coverage should be driven by what the sources actually support, not by matching the old KB one-for-one.

If the current raw corpus supports fewer or differently scoped pages than the old KB, the regenerated KB should reflect that honestly.

### 6. Missing Information Handling

When evidence is incomplete, do not smooth over the gap.

Create open-question pages for issues such as:

- unresolved curriculum sequencing
- unclear differentiation between age bands or programs
- missing operational details for supplementary programs
- any topic where prior KB structure implied certainty that the current raw files do not support

Open questions should remain specific and actionable.

### 7. Manifest Requirements

The regeneration pass must rebuild the JSON manifest and make it more useful for lookup agents.

Per-page manifest records should include at least:

- `id`
- `type`
- `title`
- `status`
- `confidence`
- `path`
- `claim_label`
- `source_refs`
- `related_pages`
- `domain_tags`
- `keywords`
- `summary`

`keywords`

- retrieval-oriented phrases, aliases, and likely search terms
- should help an agent quickly locate relevant pages without reading the full page body

`summary`

- compact article-level synopsis
- should be strong enough for fast scanning by an agent deciding which pages to open next

The manifest should remain deterministic and derived from the current KB state.

### 8. Manifest Content Quality

The new `summary` field should not be generic boilerplate.

It should capture the page’s core substance in a compact way, for example:

- what the page is about
- why it matters
- what practical angle it covers when relevant

The `keywords` field should prefer a few high-signal terms rather than noisy lists.

### 9. Rebuild Sequence

After KB regeneration:

1. rebuild indexes and reports
2. rebuild the JSON manifest
3. validate link-map integrity

This keeps the human-readable and machine-readable layers in sync.

## Expected Outcome

After the pass:

- `kb/` exists again as a usable linked knowledge base
- the pages are denser and more source-informative than before
- example source pages preserve the markdown lesson format explicitly
- lookup agents can use manifest `summary` and `keywords` to find relevant pages quickly
- unsupported details remain surfaced as gaps or open questions instead of being silently restored

## Implementation Notes

The implementation will likely need to touch:

- manual KB page creation under `kb/`
- `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
- KB rebuild tests

This change is expected to be substantive because it includes both KB content regeneration and manifest-schema improvements.
