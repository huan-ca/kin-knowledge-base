# Developer Instructions

This file gives example Codex instructions for the main actions in this repository.

Use these prompts from the repo root unless you have a reason to scope the work more narrowly.

## Bootstrap a New Repository

Example request:

```text
Use the llm-knowledge-base skill to initialize this repo as an LLM wiki repository. Create the standard layout, starter config, and state files.
```

Expected result:

- `knowledge-base.yaml`
- `raw/`
- `kb/`
- `generated/`
- `published/`
- `.kb-state/`

## Detect New or Changed Raw Files

Example request:

```text
Use the llm-knowledge-base skill to scan raw/ for file changes, update the manifest, and tell me which files are new, changed, unchanged, or removed.
```

Expected actions:

- run `update_manifest.py`
- run `plan_ingestion.py`
- summarize the ingestion plan

## Ingest Raw Material Into the Knowledge Base

Example request:

```text
Use the llm-knowledge-base skill to ingest all pending files from raw/ into kb/. Create source pages, atomic knowledge pages, and open-question pages where information is missing.
```

Operator expectation:

- preserve provenance to source chunks
- assign confidence conservatively
- do not invent unsupported details
- propose new domain types instead of silently canonizing them

## Rebuild Indexes and Reports

Example request:

```text
Use the llm-knowledge-base skill to rebuild the knowledge-base indexes, link map, gap report, conflict report, and improvement report.
```

Expected actions:

- run `rebuild_indexes.py`
- refresh:
  - `kb/index.md`
  - `generated/reports/gap-report.md`
  - `generated/reports/conflict-report.md`
  - `generated/reports/improvement-report.md`
  - `.kb-state/link-map.json`

## Generate Client-Facing Deliverables

Example requests:

```text
Use the llm-knowledge-base skill to generate a curriculum from kb/ for the configured domain. Cite source basis, include confidence, and call out any missing prerequisites.
```

```text
Use the llm-knowledge-base skill to generate lesson plans from kb/ for the current curriculum units. If the KB lacks enough information, say exactly what is missing.
```

```text
Use the llm-knowledge-base skill to generate a gap report and suggested improvements for the current raw material and normalized KB.
```

```text
Use the llm-knowledge-base skill to draft policy or culture guidance from kb/, and label any inferred sections clearly.
```

## Missing Information Policy

Example request:

```text
Generate the requested document from kb/, but do not fill in unsupported details. If the source material is incomplete, explain the gaps and what evidence would be needed.
```

Expected behavior:

- no silent fabrication
- explicit missing-information notes
- confidence-aware output
- direct mention of unsupported sections

## Safe Mental Model

Use this sequence:

1. `raw/` holds evidence.
2. `kb/` holds normalized knowledge.
3. `generated/` holds reproducible outputs.
4. `published/` holds human-maintained outputs.

When in doubt, generate from `kb/`, not from `raw/`.
