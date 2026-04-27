# Jobs

This directory holds human-owned generation inputs.

Each reusable generation workspace should live under `jobs/<job-name>/`.

Required files:
- `job.yaml`: declarative control data for the job
- `notes.md`: human-authored purpose, instructions, Q&A, and notes

Optional inputs:
- `examples/`: human-owned example outputs grouped by file type for prompt/style guidance

Recommended example layout:
- `jobs/<job-name>/examples/fully-scripted-session/`
- `jobs/<job-name>/examples/coach-guide/`
- `jobs/<job-name>/examples/quick-outline/`
- `jobs/<job-name>/examples/curriculum/`

If a job uses examples, keep the files inside its own job directory and reference them from `job.yaml` under `inputs.examples`.

Run a job with:

```bash
python3 skills/llm-knowledge-base/scripts/run_generation.py . --job-name <job-name>
```

The runner reads the job files and writes derived outputs under `generated/<job-name>/`.
Examples remain input-side artifacts in `jobs/`; they are not generated output.
