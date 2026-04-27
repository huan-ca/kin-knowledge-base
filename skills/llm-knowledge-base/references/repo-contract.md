# Repo Contract

Treat the target repo as a split between evidence, policy, derived knowledge, and human-owned outputs.

- `knowledge-base.yaml` is human-owned policy.
- `raw/` is immutable source evidence.
- `kb/` is Codex-managed normalized knowledge.
- `jobs/` is human-owned generation input for reusable job briefs, Q&A, and optional job-local examples.
- `generated/` is derived output safe to regenerate.
- `published/` is for human-maintained documents that should no longer be overwritten.
- `.kb-state/` stores manifests, plans, link maps, and ingestion history.

Never edit files in `raw/`.
Never hide missing information by filling it in silently.
Prefer regeneration of `kb/` and `generated/` over manual patching.
Generation may read `kb/` and `jobs/`, including `jobs/<job-name>/examples/`, but should never write back into `kb/`.
