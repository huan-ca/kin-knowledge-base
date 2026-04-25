---
name: llm-knowledge-base
description: Bootstrap and maintain a codex-managed linked markdown knowledge base from raw source files plus root configuration. Use when Codex needs to create an "LLM wiki", ingest raw documents into a normalized knowledge base, track file hashes and ingestion state, rebuild indexes or reports, or generate downstream artifacts such as curriculum, lesson plans, gap reports, improvement reports, policy drafts, or culture documents while preserving provenance, confidence, and explicit missing-information handling.
---

# LLM Knowledge Base

## Overview

Use this skill to create and maintain a repo-local knowledge base that separates evidence in `raw/` from normalized knowledge in `kb/`, reproducible outputs in `generated/`, and operational state in `.kb-state/`.

If the request needs facts the KB does not support, do not invent them. Surface the missing information as an `open-question`, gap report entry, or direct explanation to the user.

## Quick Start

For a new repo:

```bash
python3 skills/llm-knowledge-base/scripts/init_repo.py .
```

For new or replaced raw files:

```bash
python3 skills/llm-knowledge-base/scripts/update_manifest.py .
python3 skills/llm-knowledge-base/scripts/plan_ingestion.py .
```

After adding or editing `kb/` pages:

```bash
python3 skills/llm-knowledge-base/scripts/rebuild_indexes.py .
```

## Repo Contract

Follow `references/repo-contract.md`.

- `knowledge-base.yaml` is human-owned policy.
- `raw/` is immutable evidence.
- `kb/` is Codex-managed normalized knowledge.
- `generated/` is reproducible output.
- `published/` is human-maintained output.
- `.kb-state/` is operational memory.

## Workflow

### 1. Bootstrap

Run `scripts/init_repo.py` at repo root to create the standard layout and starter state files.
Do not move config into `kb/`; keep `knowledge-base.yaml` at repo root because it is policy, not generated knowledge.

### 2. Detect raw-file changes

Users may copy or unzip files directly into `raw/`.
Run `scripts/update_manifest.py` to hash the current raw files and update `.kb-state/raw-manifest.json`.
Run `scripts/plan_ingestion.py` to separate files into `to_ingest`, `unchanged`, and `removed`.

Treat removed files as review items. Do not silently delete derived KB pages.

### 3. Normalize knowledge into `kb/`

Create atomic markdown pages in `kb/` using the templates in `assets/templates/pages/`.
Create one `source` page per raw artifact.
Break synthesized knowledge into small pages with explicit links and source references.

Use:

- `source.md` for source artifacts
- `knowledge-page.md` for `concept`, `procedure`, `glossary-term`, and `decision`
- `domain-page.md` for configured domain-specific page types
- `open-question.md` for missing or ambiguous information
- `report.md` for generated analytical outputs

### 4. Rebuild derived indexes and reports

After changing `kb/`, run `scripts/rebuild_indexes.py`.
This refreshes:

- `kb/index.md`
- `generated/reports/gap-report.md`
- `generated/reports/conflict-report.md`
- `generated/reports/improvement-report.md`
- `.kb-state/link-map.json`

### 5. Generate downstream artifacts

Generate curriculum, lesson plans, policy drafts, culture docs, and reports from `kb/`, not directly from `raw/`.
Use `references/output-patterns.md` for output expectations.
Every generated artifact should surface provenance, confidence, and missing prerequisites.

## Page Types

Follow `references/page-types.md`.

Use universal page types for shared structure:

- `source`
- `concept`
- `procedure`
- `glossary-term`
- `decision`
- `open-question`
- `report`

Use domain-specific page types from `knowledge-base.yaml`.
If the taxonomy is insufficient, propose new types instead of silently making them canonical.

## Provenance and Confidence

Follow `references/provenance-and-confidence.md`.

Every substantive page should include:

- source references
- a confidence score
- a conservative distinction between `fact`, `inference`, `editorial-normalization`, and `open-question`
- an explicit record of missing information when the evidence is incomplete

If two sources conflict, preserve both claims, reduce confidence, and create an `open-question` or conflict report entry.
