# Client Repository Overview

This repository is used to turn client source material into structured, reviewable deliverables.

If you are a client, the main place to look is `generated/`. That directory contains the outputs produced from your source files, such as curriculum, lesson plans, reports, and other documents prepared for review.

## Directory Map

- `generated/`
  The primary client-facing output area. This is where generated deliverables are written.

- `published/`
  Documents that have moved beyond generation and are being maintained manually as working or finalized versions.

- `raw/`
  Original source files provided for the project. These are kept as evidence and are not meant to be edited during processing.

- `kb/`
  The internal knowledge base derived from the raw files. It is organized as linked markdown pages and used to support consistent downstream generation.

- `.kb-state/`
  Internal tracking data used to monitor file hashes, ingestion history, planning state, and other operational metadata.

- `skills/`
  The Codex skill and helper scripts that define how the repository is initialized, maintained, and regenerated.

- `tests/`
  Automated checks for the repository tooling and skill behavior.

- `docs/`
  Internal design and implementation notes for the repository tooling.

## How the Repo Works

In broad terms, source files are placed in `raw/`, normalized into the internal knowledge base in `kb/`, and then used to produce client-facing outputs in `generated/`.

The internal directories exist to make the output more reliable, traceable, and easier to regenerate when new source files are added or existing files change.
