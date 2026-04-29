# KB Manifest JSON Design

## Context

The repository already generates a human-readable KB index at:

- `kb/index.md`

That file is useful for browsing, but there is no direct machine-readable companion artifact that exposes the same inventory in structured form.

The repository does already maintain internal operational JSON under `.kb-state/`, but those files serve process/state responsibilities rather than acting as a stable, user-facing KB manifest.

The user wants a JSON version of the KB manifest and agreed on the name:

- `kb-manifest.json`

The agreed output boundary is:

- `generated/kb-manifest.json`

## Goal

Generate a machine-readable KB manifest at `generated/kb-manifest.json` as the JSON companion to `kb/index.md`.

## Non-Goals

- Do not move manifest data into `.kb-state/`.
- Do not replace `kb/index.md`.
- Do not add a new job-scoped output for this.
- Do not make `kb/` hold generated JSON artifacts.

## Chosen Approach

Extend the index rebuild process so it emits both:

- `kb/index.md`
- `generated/kb-manifest.json`

The manifest should be derived from the same validated page set already used to build the markdown index.

That keeps the markdown and JSON views aligned and avoids introducing a separate inventory pipeline.

## Output Location

The manifest should be written to:

- `generated/kb-manifest.json`

This keeps the boundary clean:

- `kb/` remains human-readable markdown knowledge
- `.kb-state/` remains internal operational state
- `generated/` remains reproducible derived artifacts

## Manifest Structure

The JSON should contain:

- top-level summary counts by page type
- a flat list of page records

Recommended top-level shape:

```json
{
  "page_counts": {
    "concept": 14,
    "lesson": 2
  },
  "pages": [
    {
      "id": "double-leg-side-control-americana-example-lesson",
      "type": "lesson",
      "title": "Double Leg to Side Control to Americana Example Lesson",
      "status": "active",
      "confidence": 0.6,
      "path": "kb/lessons/double-leg-side-control-americana-example-lesson.md",
      "claim_label": "editorial-normalization",
      "source_refs": ["source-example-scripted-lesson-plan-adult#chunk-001"],
      "related_pages": []
    }
  ]
}
```

## Required Fields

Each page record should include at least:

- `id`
- `type`
- `title`
- `status`
- `confidence`
- `path`

It should also include, where already available from the validated page metadata:

- `claim_label`
- `source_refs`
- `related_pages`

## Ordering

The JSON should be deterministic.

That means:

- `page_counts` keys sorted consistently
- `pages` sorted consistently, preferably by type then title, matching the general markdown index ordering
- stable formatting with normal JSON indentation

## Relationship To `kb/index.md`

`kb/index.md` remains the human-friendly view.

`generated/kb-manifest.json` becomes the machine-readable companion view.

Both should be derived from the same source page inventory during the rebuild step so they cannot silently diverge.

## Testing and Verification

Tests should verify:

- `rebuild_indexes.py` writes `generated/kb-manifest.json`
- the manifest includes `page_counts`
- the manifest includes page records with required fields
- the manifest path values point at KB markdown files
- output is deterministic for the same KB input set

Manual verification should include opening:

- `kb/index.md`
- `generated/kb-manifest.json`

and confirming they describe the same KB inventory.

## Files Likely In Scope

- `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
- `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`

No broader generation or ingestion refactor is required for this change.
