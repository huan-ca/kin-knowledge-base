# Agent Guide

This repository uses Codex with the repo-local `llm-knowledge-base` skill to build and maintain linked markdown knowledge bases and to generate downstream documents from them.

The skill does not need to be installed into the global Codex skill directory for work in this repository. Codex can read and use it directly from the filesystem at `skills/llm-knowledge-base/`.

## Agent Purpose

The agent’s job is to:

- treat `raw/` as immutable source evidence
- normalize that evidence into atomic, linked markdown pages in `kb/`
- maintain reproducible outputs in `generated/`
- preserve provenance, confidence, and explicit gap reporting
- avoid fabricating missing facts

## Operating Model

The intended flow is:

1. Source files are added to `raw/`.
2. Codex updates the raw-file manifest and identifies new, changed, unchanged, or removed files.
3. Codex ingests supported source material into `kb/` as structured pages.
4. Codex rebuilds indexes and reports.
5. Codex generates downstream artifacts from `kb/`, not directly from `raw/`.

## Required Behaviors

- `knowledge-base.yaml` is policy, not generated content.
- `raw/` must never be edited by the agent.
- `kb/` and `generated/` are treated as derived and reproducible.
- `published/` is human-owned and should not be overwritten automatically.
- Every substantive KB page should carry `claim_label`, `source_refs`, and `confidence`.
- Missing prerequisites must be surfaced clearly instead of guessed.

## Confidence and Provenance

The agent should distinguish between:

- `fact`
- `inference`
- `editorial-normalization`
- `open-question`

If evidence is weak, ambiguous, or conflicting, the agent should lower confidence and produce explicit gap or conflict records rather than smoothing over the issue.

## Typical Outputs

Depending on repository configuration and source material, the agent may generate:

- curriculum
- lesson plans
- gap reports
- improvement reports
- policy drafts
- culture or team-guideline documents

## Main Skill Assets

The primary skill lives at [skills/llm-knowledge-base/SKILL.md](/Users/huan/dev/kin/skills/llm-knowledge-base/SKILL.md).

When working in this repo, point Codex at that file-system path and use the skill from there. Installation into `~/.codex/skills` is optional and only needed if you want it to appear as a globally available named skill in future sessions.

Key helper scripts:

- [skills/llm-knowledge-base/scripts/init_repo.py](/Users/huan/dev/kin/skills/llm-knowledge-base/scripts/init_repo.py)
- [skills/llm-knowledge-base/scripts/update_manifest.py](/Users/huan/dev/kin/skills/llm-knowledge-base/scripts/update_manifest.py)
- [skills/llm-knowledge-base/scripts/plan_ingestion.py](/Users/huan/dev/kin/skills/llm-knowledge-base/scripts/plan_ingestion.py)
- [skills/llm-knowledge-base/scripts/rebuild_indexes.py](/Users/huan/dev/kin/skills/llm-knowledge-base/scripts/rebuild_indexes.py)
