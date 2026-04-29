# KB Manifest Location Design

## Context

The repository currently emits a machine-readable KB manifest at:

- `generated/kb-manifest.json`

That location was chosen as a general derived-output boundary, but the user clarified the actual consumer: deterministic code that loads KB structure directly and uses it as an article registry for fast reference and asset lookup in agent workflows.

For that use case, the manifest should live beside the KB it indexes rather than under the broader `generated/` tree.

The desired location is:

- `kb/kb-manifest.json`

## Goal

Move the canonical machine-readable KB manifest from `generated/kb-manifest.json` to `kb/kb-manifest.json`.

## Non-Goals

- Do not change the manifest schema unless needed for the move.
- Do not keep duplicate copies in both `kb/` and `generated/`.
- Do not move operational state into `.kb-state/`.
- Do not replace `kb/index.md`.

## Chosen Approach

Change the rebuild contract so it writes:

- `kb/index.md`
- `kb/kb-manifest.json`

and stops writing:

- `generated/kb-manifest.json`

This keeps the human-readable and machine-readable KB inventories side by side under `kb/`.

## Rationale

This boundary better fits deterministic loading and registry usage:

- the manifest lives beside the markdown assets it indexes
- consumers do not need to traverse out to `generated/`
- the KB directory becomes a self-contained content-plus-registry surface for agent code

The JSON file remains generated, but it is generated into the KB surface because that surface is the thing agent code wants to load.

## Output Contract

After rebuild, the expected KB inventory artifacts are:

- `kb/index.md`
- `kb/kb-manifest.json`

No `generated/kb-manifest.json` should be emitted.

## Manifest Content

The manifest content can remain the same:

- `page_counts`
- `pages`

Each page record should continue to include:

- `id`
- `type`
- `title`
- `status`
- `confidence`
- `path`
- `claim_label`
- `source_refs`
- `related_pages`

## Determinism

The moved manifest should remain deterministic:

- stable path
- stable JSON formatting
- stable page ordering
- stable count ordering

## Testing and Verification

Tests should verify:

- rebuild writes `kb/kb-manifest.json`
- rebuild no longer depends on `generated/kb-manifest.json`
- the manifest includes the expected schema
- manifest paths still point at KB markdown files

Manual verification should include:

- opening `kb/index.md`
- opening `kb/kb-manifest.json`
- confirming the manifest is usable as a local KB registry

## Files Likely In Scope

- `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
- `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`

No broader generation or ingestion refactor is required for this boundary move.
