# Generation Runner Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the curriculum-only generation entrypoint with a generic job runner and repo-local generator registry while preserving current curriculum output behavior.

**Architecture:** Keep the `llm-knowledge-base` skill generic by moving document-family logic into `repo_generators/` modules and routing all job execution through a single `run_generation.py` entrypoint. Convert the existing curriculum job to a declarative `job.yaml`, keep optional human notes in markdown, and write run metadata under each job’s generated output tree.

**Tech Stack:** Python scripts, markdown/yaml job specs, pytest

---

### Task 1: Add Failing Tests For The Generic Runner

**Files:**
- Modify: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`
- Create: `tests/skills/llm_knowledge_base/test_run_generation.py`

- [ ] **Step 1: Write the failing test for generic job execution**

```python
def test_run_generation_executes_curriculum_job_from_job_yaml(tmp_path):
    ...
    result = subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (repo / "generated" / "weekly-curriculum" / "_meta" / "run.json").exists()
```

- [ ] **Step 2: Write the failing test for reserved generator handling and metadata**

```python
def test_run_generation_rejects_unknown_generator(tmp_path):
    ...
    assert result.returncode != 0
    assert "unknown generator" in result.stderr
```

- [ ] **Step 3: Update curriculum generator tests to call the generic runner instead of the legacy curriculum script**

```python
RUN_SCRIPT = Path("skills/llm-knowledge-base/scripts/run_generation.py").resolve()
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `pytest tests/skills/llm_knowledge_base/test_run_generation.py tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`
Expected: FAIL because `run_generation.py`, `job.yaml` loading, and registry-backed execution do not exist yet.

- [ ] **Step 5: Commit**

```bash
git add tests/skills/llm_knowledge_base/test_run_generation.py tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py
git commit -m "test: cover generic job runner"
```

### Task 2: Introduce The Generic Runner And Registry

**Files:**
- Create: `repo_generators/__init__.py`
- Create: `repo_generators/registry.py`
- Create: `repo_generators/curriculum.py`
- Create: `skills/llm-knowledge-base/scripts/run_generation.py`
- Modify: `skills/llm-knowledge-base/scripts/common.py`

- [ ] **Step 1: Create the generator result shape and registry**

```python
GENERATOR_REGISTRY = {
    "curriculum": "repo_generators.curriculum",
}
```

- [ ] **Step 2: Move the current curriculum generation logic into `repo_generators/curriculum.py`**

```python
def generate(repo_root: Path, job_spec: dict, job_context: dict) -> dict:
    ...
    return {
        "outputs": output_paths,
        "warnings": [],
        "new_facts_count": len(records),
    }
```

- [ ] **Step 3: Implement `run_generation.py` as the only job entrypoint**

```python
parser.add_argument("repo_root")
parser.add_argument("--job-name", required=True)
...
job_spec = load_job_spec(...)
generator = load_generator(job_spec["generator"])
result = generator.generate(...)
write_run_metadata(...)
```

- [ ] **Step 4: Add shared helpers for yaml-ish parsing or structured job loading without pulling in unnecessary dependencies**

```python
def load_simple_yaml(path: Path) -> dict[str, Any]:
    ...
```

- [ ] **Step 5: Run tests to verify the new runner passes**

Run: `pytest tests/skills/llm_knowledge_base/test_run_generation.py tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add repo_generators skills/llm-knowledge-base/scripts/run_generation.py skills/llm-knowledge-base/scripts/common.py
git commit -m "feat: add generic job runner and registry"
```

### Task 3: Convert The Existing Job To Declarative Input And Add Run Metadata

**Files:**
- Modify: `jobs/README.md`
- Replace: `jobs/kin-bjj-weekly-curriculum/job.md`
- Create: `jobs/kin-bjj-weekly-curriculum/job.yaml`
- Create: `jobs/kin-bjj-weekly-curriculum/notes.md`
- Modify: `generated/kin-bjj-weekly-curriculum/_meta/run.json`
- Modify: `skills/llm-knowledge-base/SKILL.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Convert the current job control data into `job.yaml`**

```yaml
id: kin-bjj-weekly-curriculum
title: KIN BJJ Weekly Curriculum
generator: curriculum
generation_targets:
  - curriculum
status: active
transient: false
inputs:
  kb_pages:
    - kb/curriculum/youth-24-week-theme-map.md
    - kb/curriculum/adult-24-week-theme-map.md
    - kb/curriculum/tots-12-week-theme-map.md
options:
  include_reports: true
  emit_new_facts: true
```

- [ ] **Step 2: Move the narrative guidance into `notes.md`**

```md
# KIN BJJ Weekly Curriculum Notes
...
```

- [ ] **Step 3: Regenerate the curriculum job through the generic runner and emit `_meta/run.json`**

Run: `python3 skills/llm-knowledge-base/scripts/run_generation.py . --job-name kin-bjj-weekly-curriculum`
Expected: updated `generated/kin-bjj-weekly-curriculum/` plus `_meta/run.json`

- [ ] **Step 4: Update skill and agent docs to point to the generic runner**

```md
- `skills/llm-knowledge-base/scripts/run_generation.py`
```

- [ ] **Step 5: Commit**

```bash
git add jobs/README.md jobs/kin-bjj-weekly-curriculum/job.yaml jobs/kin-bjj-weekly-curriculum/notes.md generated/kin-bjj-weekly-curriculum/_meta/run.json skills/llm-knowledge-base/SKILL.md AGENTS.md
git commit -m "feat: convert curriculum job to declarative runner input"
```

### Task 4: Add Compatibility Shim And Final Verification

**Files:**
- Modify: `skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py`
- Modify: `tests/skills/llm_knowledge_base/test_skill_docs.py`

- [ ] **Step 1: Replace the old curriculum script body with a thin compatibility shim**

```python
from run_generation import main

if __name__ == "__main__":
    main(default_generator="curriculum")
```

- [ ] **Step 2: Keep current script invocation working for existing users**

```bash
python3 skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py . --job-name kin-bjj-weekly-curriculum
```

- [ ] **Step 3: Run the full KB test suite**

Run: `pytest tests/skills/llm_knowledge_base -q`
Expected: PASS

- [ ] **Step 4: Spot-check the generated job metadata and output tree**

Run: `find generated/kin-bjj-weekly-curriculum -maxdepth 2 -type f | sort | sed -n '1,30p'`
Expected: includes `_meta/run.json`, `reports/*.md`, `new-facts/index.md`, and curriculum files

- [ ] **Step 5: Commit**

```bash
git add skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py tests/skills/llm_knowledge_base/test_skill_docs.py
git commit -m "refactor: keep curriculum generator as compatibility shim"
```
