# LLM Knowledge Base Skill Design

## Goal

Create a reusable Codex skill that bootstraps and maintains a repo-local "LLM Knowledge Base" following an LLM wiki pattern inspired by Andrej Karpathy's "LLM Wiki" approach:

- many small markdown pages
- explicit linking between pages
- strict folder taxonomy
- standardized metadata/templates
- generated indexes/maps
- clear separation between source evidence and synthesized knowledge

The skill must be generic enough to reuse in other repos and domains, while still supporting domain-specific extensions through configuration.

## Primary Outcomes

The skill should enable Codex to:

1. Bootstrap a knowledge-base repo layout and root config
2. Ingest raw source files from `raw/` into a normalized markdown wiki in `kb/`
3. Track raw file changes with manifests and content hashes
4. Rebuild codex-managed knowledge pages deterministically from `raw/` plus config
5. Generate downstream artifacts such as curriculum, lesson plans, gap reports, improvement reports, and optionally policy/culture documents
6. Refuse to fabricate unsupported content and instead surface explicit gaps, open questions, and confidence limitations

## Recommended Approach

Adopt a combined model:

- one primary skill
- one repo contract
- one set of helper scripts for deterministic operations

The skill should cover two workflows:

1. Bootstrap workflow
   Create the repo structure, root config, templates, and state files.
2. Ingestion and maintenance workflow
   Detect raw-file changes, ingest content into `kb/`, rebuild reports/indexes, and generate downstream outputs.

This should remain a single skill rather than splitting bootstrap and ingestion into separate skills, because both workflows share the same repo contract, provenance rules, confidence rules, and operational state.

## Repo Contract

The repo layout should be:

- `knowledge-base.yaml`
  Human-owned root configuration and policy file. This defines domain name, canonical domain types, required metadata, confidence rubric, output targets, and generation constraints.

- `raw/`
  Human-managed immutable source evidence. Users can copy or unzip source artifacts here directly. Codex does not edit files in this directory.

- `kb/`
  Codex-managed derived markdown wiki. This contains normalized, atomic, linked knowledge pages generated from `raw/` plus `knowledge-base.yaml`. This directory should be safe to regenerate.

- `generated/`
  Codex-generated derived outputs such as curriculum, lesson plans, reports, policy drafts, and culture docs. These should be reproducible from `kb/`.

- `published/` or `working/`
  Human-owned output area for documents that originated from generated artifacts but should no longer be overwritten automatically.

- `.kb-state/`
  Codex-managed operational state, including raw-file manifests, hashes, ingestion batches, prior ingestion metadata, conflict tracking, and index build state.

### Directory Semantics

- `raw/` is evidence
- `knowledge-base.yaml` is policy
- `kb/` is normalized knowledge
- `generated/` is reproducible output
- `published/working/` is human-maintained output
- `.kb-state/` is operational memory

## Knowledge Model

The skill should enforce a hybrid knowledge model:

- universal page types shared across repos
- domain-specific page types configured in `knowledge-base.yaml`

### Universal Page Types

- `source`
  One raw artifact and its ingestion metadata
- `concept`
  Stable units of explanatory knowledge
- `procedure`
  Stepwise methods or workflows
- `glossary-term`
  Canonical definitions
- `decision`
  Explicit editorial or structural normalization decisions
- `open-question`
  Missing, ambiguous, unresolved, or conflicting knowledge requiring follow-up
- `report`
  Generated analytical pages such as gap analyses, confidence summaries, or conflict summaries

### Domain-Specific Page Types

Defined in `knowledge-base.yaml`.

For the BJJ use case, example domain types may include:

- `position`
- `submission`
- `escape`
- `transition`
- `drill`
- `lesson`
- `curriculum-unit`

### Controlled Type Extension

Canonical domain types come from config. Codex may detect recurring content that does not fit existing types, but it should not freely invent canonical types during ingestion.

Allowed behavior:

- propose candidate new types
- record proposals in reports or `.kb-state/`
- map content to the nearest canonical type plus tags until a human approves the new type

Disallowed default behavior:

- silently creating new canonical page types without approval

## Page Design Rules

Every knowledge page in `kb/` should be:

- atomic
- link-rich
- provenance-backed
- confidence-scored
- explicit about uncertainty

### Page Metadata

Recommended core metadata:

- page ID
- page type
- title
- status
- confidence score
- claim labels where needed
- source references
- related pages
- domain tags
- ingestion batch/version
- supersedes / superseded-by references where relevant

### Claim Labels

The system should distinguish:

- `fact`
- `inference`
- `editorial-normalization`
- `open-question`

If a requested generated output requires information that the KB does not actually support, Codex should say so explicitly and identify the missing prerequisites.

## Provenance and Confidence

Reliable generation requires traceability and explicit uncertainty.

### Provenance Rules

- every raw file gets a `source` page
- every atomic KB page references one or more source chunks
- generated outputs include a source basis section or equivalent citation map
- changed sources remain traceable across ingestion history
- superseded material is preserved in state/history rather than disappearing silently

### Confidence Rules

- every KB page carries a confidence score
- the confidence rubric lives in `knowledge-base.yaml`
- confidence drops when content is weakly supported, ambiguous, conflicting, sparsely sourced, or materially inferred
- generated outputs surface low-confidence sections rather than presenting them as settled

## Gap and Conflict Handling

The system must not hide incompleteness.

### Gap Behavior

- missing required information becomes an `open-question` page or a generated gap report entry
- if a request cannot be satisfied from the KB, Codex explicitly says so and points to the missing information
- improvement reports should suggest where better source material, explicit decisions, or taxonomy changes would improve generation quality

### Conflict Behavior

- no silent overwrite of competing claims
- preserve both claims and their provenance
- create explicit conflict records or unresolved question records
- lower confidence until the conflict is resolved

## Ingestion Workflow

New files should be ingested through an explicit workflow. Copying files into `raw/` is allowed and expected, but that does not itself perform ingestion.

### Ingestion Sequence

1. User copies or unzips raw artifacts into `raw/`
2. Codex scans `raw/` and updates a manifest in `.kb-state/`
3. Manifest entries record relative path, content hash, file size, timestamp, import batch ID, ingestion status, linked source page ID, and last-ingested hash
4. Codex compares the current scan to prior manifest state
5. New or changed files are marked for ingestion
6. Unchanged files are skipped
7. Removed files are flagged for review rather than triggering silent KB deletions
8. For selected files, Codex creates or updates `source` pages and derives atomic KB pages in `kb/`
9. Codex rebuilds indexes, reports, gaps, open questions, and conflict summaries
10. Codex generates downstream files from `kb/`, never directly from `raw/`

## Change Detection and History

The system should support full-bundle replacement in `raw/`, including unzipped source dumps where the user does not know which files changed.

### Required State Tracking

The manifest or state layer should track at least:

- relative path
- content hash
- file size
- modified timestamp
- source bundle/import batch ID
- ingestion status
- last-ingested hash
- linked `source` page ID

### Versioning Policy

When a raw file changes:

- latest version becomes canonical for future generation
- prior ingestion metadata is preserved
- materially superseded knowledge stays traceable through provenance/history
- unresolved changes or contradictions reduce confidence rather than being hidden

## Regeneration Policy

Codex owns regeneration for derived areas.

- `kb/` is codex-managed and regenerable from `raw/` plus `knowledge-base.yaml`
- `generated/` is derived and reproducible by default
- `published/working/` is outside automatic overwrite behavior
- config remains at repo root rather than inside `kb/`, because config is policy, not generated knowledge

## Skill Contents

The skill should ship with both instructions and deterministic helper scripts.

### Responsibilities

- bootstrap repo structure
- create root config and starter templates
- scan `raw/` and update file-hash manifest
- detect new, changed, removed, and unchanged files
- create/update `source` pages
- scaffold atomic KB pages from normalized knowledge
- rebuild indexes and reports
- generate downstream artifacts from `kb/`
- refuse unsupported generation and emit explicit gaps

### Recommended Bundled Scripts

- `scripts/init_repo.py`
  Initialize `knowledge-base.yaml`, `raw/`, `kb/`, `generated/`, `published/`, and `.kb-state/`

- `scripts/update_manifest.py`
  Hash files in `raw/` and update manifest state

- `scripts/plan_ingestion.py`
  Compare current and prior state to identify new, changed, removed, and unchanged files

- `scripts/rebuild_indexes.py`
  Rebuild indexes, link maps, and report scaffolds from `kb/`

### Recommended References

- `references/repo-contract.md`
- `references/page-types.md`
- `references/provenance-and-confidence.md`
- `references/output-patterns.md`

### Recommended Assets

- `assets/templates/`
  Templates for `source`, `concept`, `procedure`, `glossary-term`, `decision`, `open-question`, `report`, and example domain pages

## Generation Targets

The skill should support downstream generation from `kb/` for:

- curriculum
- lesson plans
- gap reports
- suggested improvement reports
- policy drafts
- culture or culture-building documents

Generation must honor:

- source basis
- confidence
- open gaps
- conflict visibility

If the KB lacks required information, Codex must not invent content without disclosure.

## Non-Goals for First Version

The initial skill does not need to solve every parsing problem or provide perfect automatic extraction from all document formats.

The first version should prioritize:

- repo contract
- deterministic manifests and change detection
- page scaffolding and structure
- provenance/confidence discipline
- rebuildable indexes and reports

Content extraction and normalization can initially rely on Codex-guided ingestion with helper-script support around stateful operations.

## Open Implementation Decisions

These points are intentionally left for the implementation plan rather than the design:

- exact `knowledge-base.yaml` schema
- exact markdown frontmatter schema for KB pages
- exact manifest JSON/YAML schema in `.kb-state/`
- confidence scoring algorithm and rubric defaults
- whether to add optional helper commands for generating specific outputs like curriculum or lesson plans

## Recommendation

Build one reusable skill that establishes a strict repo contract, a hybrid knowledge model, deterministic raw-file change detection, codex-managed regeneration, explicit provenance/confidence/gap handling, and reusable helper scripts for stateful operations.
