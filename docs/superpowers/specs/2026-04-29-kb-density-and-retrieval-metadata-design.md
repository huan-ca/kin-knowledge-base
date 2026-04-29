# KB Density And Retrieval Metadata Design

## Summary

The current KB page templates and guidance encourage compression. Pages often collapse into a short definition and a few bullets, which makes the KB readable but too information-poor for strong downstream generation.

This change raises the default information floor of substantive KB pages and adds retrieval-oriented metadata to the KB manifest. The goal is to make KB pages denser and more reusable without forcing every page into a heavy, training-specific structure.

## Problem

The existing default page shapes bias the KB toward terse summaries:

- `knowledge-page.md` centers on `Canonical Statement` and `Supporting Evidence`
- `domain-page.md` centers on `Definition` and `Key Details`

That pattern creates several downstream problems:

- generated artifacts inherit overly compressed phrasing
- pages preserve fewer examples, distinctions, and implications than the sources support
- retrieval depends too heavily on titles and page types
- generators have weak signals for selecting nearby relevant pages

## Goals

- Make substantive KB pages denser by default
- Preserve more source-backed distinctions, implications, and usable detail
- Keep pages atomic while improving each page as a retrieval unit
- Add manifest metadata that helps generators select relevant pages deterministically
- Avoid forcing practice-specific sections onto abstract pages that do not need them

## Non-Goals

- Rewriting existing KB pages in this change
- Re-running ingestion or generation as part of this change
- Adding new canonical domain types
- Replacing source provenance requirements

## Design

### 1. New Default Page Contract

Substantive KB pages should preserve more usable detail by default.

Required baseline sections for substantive non-source pages:

- `Definition`
- `Detailed Notes`
- `Related Pages`
- `Gaps`

Optional sections when relevant:

- `Operational Implications`
- `Examples or Variants`
- `Constraints or Safety Notes`

This keeps the universal contract simple while allowing practice-oriented pages to preserve training-specific detail.

### 2. Section Semantics

`Definition`

- State what the page is about in a clear, conservative way
- Avoid overclaiming beyond the cited source material

`Detailed Notes`

- Preserve distinctions, explanations, supporting detail, and structure from the source
- Prefer several concrete bullets or short subsections over a compressed summary
- Capture what the concept means, how it is described, and what surrounding context matters

`Related Pages`

- Link nearby concepts, dependencies, adjacent procedures, and common pairings
- Help both humans and generators expand local context intentionally

`Gaps`

- Preserve missing, unclear, disputed, or under-specified areas
- Continue to favor honest provenance over smoothed-over certainty

`Operational Implications`

- Use when the page affects how a coach, student, or operator should act
- Especially useful for class structure, teaching method, curriculum, and procedural pages

`Examples or Variants`

- Use when examples, forms, contexts, or age/program variants matter to understanding
- Especially useful for BJJ instruction, class delivery, curriculum framing, and practical coaching topics

`Constraints or Safety Notes`

- Use when the idea has context limits, teaching boundaries, intensity limits, sequencing cautions, or safety implications
- Especially useful for drilling, live training, youth instruction, resistance scaling, and submission-related content

These optional sections are not mandatory on every page. Abstract pages should not be forced into awkward empty structure.

### 3. Template Changes

The page templates should be updated so the default authoring shape nudges toward richer pages.

`knowledge-page.md`

- replace `Canonical Statement` with `Definition`
- replace `Supporting Evidence` with `Detailed Notes`
- include `Related Pages`
- include `Gaps`
- include commented optional headings for:
  - `Operational Implications`
  - `Examples or Variants`
  - `Constraints or Safety Notes`

`domain-page.md`

- keep `Definition`
- replace `Key Details` with `Detailed Notes`
- include `Related Pages`
- include `Gaps`
- include the same commented optional headings for the practice-oriented sections

The templates should make the richer baseline visible while still showing that some sections are conditional.

### 4. Guidance Changes

The `llm-knowledge-base` skill guidance should explicitly instruct authors to preserve more useful source detail in each derived page.

Guidance additions should emphasize:

- do not collapse rich source material into thin summaries
- preserve distinctions, examples, and contextual implications when supported
- use optional practice-oriented sections when they materially improve retrieval and generation
- keep pages atomic, but make each page strong enough to support downstream writing with specificity

The guidance should also clarify that denser pages do not mean verbose filler. The aim is better recoverable structure, not longer prose for its own sake.

### 5. Retrieval Metadata In Page Frontmatter

The KB should expose better retrieval signals directly in page metadata.

Add or formalize:

- `domain_tags`
  - curated categorical topic labels
  - should remain short and intentional
- `keywords`
  - free-form retrieval terms, aliases, phrases, and likely search vocabulary
  - may include synonyms, common coaching phrases, and closely related search terms

`domain_tags` and `keywords` should be optional but recommended on substantive pages, especially pages likely to feed generation.

### 6. Retrieval Metadata In KB Manifest

The KB manifest should include the retrieval metadata so generator jobs can select relevant pages without reparsing markdown frontmatter from scratch.

Add manifest fields per page:

- `domain_tags`
- `keywords`

Retain existing useful fields:

- `id`
- `type`
- `title`
- `status`
- `confidence`
- `path`
- `claim_label`
- `source_refs`
- `related_pages`

If present on a page, future generators may also benefit from existing curriculum metadata such as:

- `age_group`
- `program_level`
- `teaching_goal`

But this change only requires exposing `domain_tags` and `keywords` reliably.

### 7. Generator Use Model

This design does not change generator behavior directly, but it creates a better deterministic retrieval surface.

Generators should be able to:

- filter by `type`
- narrow by `domain_tags`
- match user/job vocabulary through `keywords`
- expand local context through `related_pages`

This supports more precise page selection without inventing a second job-specific metadata system.

## Expected Outcome

After these template and guidance changes:

- new KB pages should preserve more useful source detail by default
- generated outputs should have access to richer upstream material
- generator jobs should have better manifest-level cues for page selection
- abstract topics should remain clean while practice-oriented topics can preserve operational depth

## Implementation Notes

The implementation should likely touch:

- `skills/llm-knowledge-base/assets/templates/pages/knowledge-page.md`
- `skills/llm-knowledge-base/assets/templates/pages/domain-page.md`
- `skills/llm-knowledge-base/SKILL.md`
- `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
- relevant rebuild-index tests

This change should not rewrite existing KB pages yet. Existing content can be regenerated or revised later to test whether the denser contract improves downstream outputs.
