---
name: llm-knowledge-base
description: Bootstrap and maintain a codex-managed linked markdown knowledge base from raw source files plus root configuration. Use when Codex needs to create an "LLM wiki", ingest raw documents into a normalized knowledge base, track file hashes and ingestion state, rebuild indexes or reports, or generate downstream artifacts such as curriculum, lesson plans, gap reports, improvement reports, policy drafts, or culture documents while preserving provenance, confidence, and explicit missing-information handling.
---

# LLM Knowledge Base

## Overview

Use this skill to create and maintain a repo-local knowledge base that separates evidence in `raw/` from normalized knowledge in `kb/`, human-owned generation inputs in `jobs/` including optional job-local examples, reproducible outputs in `generated/`, and operational state in `.kb-state/`.

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

For job-scoped generation:

```bash
python3 skills/llm-knowledge-base/scripts/run_generation.py . --job-name <job-name>
```

## Repo Contract

Follow `references/repo-contract.md`.

- `knowledge-base.yaml` is human-owned policy.
- `raw/` is immutable evidence.
- `kb/` is Codex-managed normalized knowledge.
- `jobs/` is human-owned generation input, including reusable job briefs, notes, and optional examples.
- `generated/` is reproducible output, typically under `generated/<job-name>/`.
- `published/` is human-maintained output.
- `.kb-state/` is operational memory.

## Workflow

### 1. Bootstrap

Run `scripts/init_repo.py` at repo root to create the standard layout and starter state files.
Do not move config into `kb/`; keep `knowledge-base.yaml` at repo root because it is policy, not generated knowledge.
Generation should never write back into `kb/`.

### 2. Detect raw-file changes

Users may copy or unzip files directly into `raw/`.
Run `scripts/update_manifest.py` to hash the current raw files and update `.kb-state/raw-manifest.json`.
Run `scripts/plan_ingestion.py` to separate files into `to_ingest`, `unchanged`, and `removed`.

Treat removed files as review items. Do not silently delete derived KB pages.

### 3. Normalize knowledge into `kb/`

Create atomic markdown pages in `kb/` using the templates in `assets/templates/pages/`.
Create one `source` page per raw artifact.
Break synthesized knowledge into small pages with explicit links and source references.

Default to a dense ingestion pass, not a minimal summary pass.

- Preserve as much supported information from `raw/` as practical.
- Prefer many small KB pages over a few broad summary pages when the source supports that decomposition.
- Expand source pages with section-level or topic-level extracted claims so downstream generation has more recoverable evidence.
- When a source contains multiple distinct operational, curriculum, policy, cultural, or technical concepts, split them into separate pages instead of collapsing them into one blended summary.
- Only use a lighter ingestion mode when the user explicitly asks for a fast, narrow, or partial pass.

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
When a repo uses job-scoped generation, load the job spec from `jobs/<job-name>/job.yaml`, optional notes from `jobs/<job-name>/notes.md`, optional examples from `jobs/<job-name>/examples/`, and emit artifacts under `generated/<job-name>/`.
Use `references/output-patterns.md` for output expectations.
Every generated artifact should surface provenance, confidence, and missing prerequisites.

## Ingestion Density

High-granularity ingestion is the default.

- Capture source detail conservatively, but capture a lot of it.
- Prefer explicit decomposition of sections, rules, procedures, frameworks, and technical systems into separate pages.
- Treat high-quality markdown or text sources as an opportunity to build a richer KB, not just a smaller summary.
- If the source is too large to finish in one pass, still maximize useful coverage and leave explicit `open-question` pages for the remainder instead of shrinking the whole ingestion effort.

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

The bootstrap policy should enforce this through `required_substantive_page_metadata` in `knowledge-base.yaml`.

If two sources conflict, preserve both claims, reduce confidence, and create an `open-question` or conflict report entry.
