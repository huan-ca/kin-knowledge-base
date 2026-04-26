# Jobs

This directory holds human-owned generation inputs.

Each reusable generation workspace should live under `jobs/<job-name>/`.

Required files:
- `job.yaml`: declarative control data for the job
- `notes.md`: human-authored purpose, instructions, Q&A, and notes

Run a job with:

```bash
python3 skills/llm-knowledge-base/scripts/run_generation.py . --job-name <job-name>
```

The runner reads the job files and writes derived outputs under `generated/<job-name>/`.
