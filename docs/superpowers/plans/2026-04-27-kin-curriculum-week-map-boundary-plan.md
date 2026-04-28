# KIN Curriculum Week-Map Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move synthesized curriculum week maps out of `kb/`, generate them under `generated/kin-bjj-weekly-curriculum/week-maps/`, and deterministically render curriculum outputs from those generated artifacts only.

**Architecture:** Refactor the curriculum generator into a two-stage flow. Stage 1 synthesizes candidate week-map artifacts from framework KB pages and job notes/examples; Stage 2 reads only those generated week maps to produce curriculum files, syllabi, reports, and fully scripted sessions. The KB index rebuild remains independent and must stop referencing the deleted week-map pages.

**Tech Stack:** Python 3, pytest, repo-local generation scripts, markdown frontmatter, fenced JSON payloads

---

### Task 1: Lock In The New Boundary With Failing Tests

**Files:**
- Modify: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`
- Modify: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`
- Reference: `repo_generators/curriculum.py`
- Reference: `skills/llm-knowledge-base/scripts/rebuild_indexes.py`

- [ ] **Step 1: Add a failing test that expects generated week maps to exist and be used**

```python
def test_generate_curriculum_outputs_write_generated_week_maps_and_render_from_them(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(repo, "weekly-curriculum", include_examples=True)

    for relative_path in (
        "kb/curriculum/youth-24-week-theme-map.md",
        "kb/curriculum/adult-24-week-theme-map.md",
        "kb/curriculum/tots-12-week-theme-map.md",
    ):
        (repo / relative_path).unlink()

    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

    week_map_path = repo / "generated" / "weekly-curriculum" / "week-maps" / "adult-24-week-theme-map.md"
    curriculum_path = repo / "generated" / "weekly-curriculum" / "curriculum" / "adult" / "week-01-curriculum.md"

    week_map_text = week_map_path.read_text(encoding="utf-8")
    curriculum_text = curriculum_path.read_text(encoding="utf-8")

    assert "type: generated-curriculum-candidate" in week_map_text
    assert "```json" in week_map_text
    assert "Adult Week 01" in curriculum_text or "# Adult Week 01 Curriculum" in curriculum_text
```

- [ ] **Step 2: Add a failing test that proves Stage 2 will not fall back to deleted KB week maps**

```python
def test_generate_curriculum_outputs_fail_when_generated_week_maps_are_missing(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(repo, "weekly-curriculum")

    for relative_path in (
        "kb/curriculum/youth-24-week-theme-map.md",
        "kb/curriculum/adult-24-week-theme-map.md",
        "kb/curriculum/tots-12-week-theme-map.md",
    ):
        (repo / relative_path).unlink()

    output_root = repo / "generated" / "weekly-curriculum"
    if output_root.exists():
        shutil.rmtree(output_root)

    completed = subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"],
        text=True,
        capture_output=True,
    )

    assert completed.returncode != 0
    assert "generated week map" in (completed.stderr + completed.stdout).lower()
```

- [ ] **Step 3: Add a failing test that verifies index rebuild no longer references removed KB week-map pages**

```python
def test_rebuild_indexes_drops_deleted_curriculum_week_maps_from_index_and_reports(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    source_page = repo / "kb" / "sources" / "overview.md"
    source_page.parent.mkdir(parents=True, exist_ok=True)
    source_page.write_text(
        \"\"\"---
id: source-overview
type: source
title: Overview
status: active
confidence: 1.0
source_refs: []
related_pages: []
---
# Overview
\"\"\",
        encoding="utf-8",
    )

    framework_page = repo / "kb" / "curriculum" / "curriculum-week-design-rules.md"
    framework_page.parent.mkdir(parents=True, exist_ok=True)
    framework_page.write_text(
        \"\"\"---
id: curriculum-week-design-rules
type: curriculum-unit
title: Curriculum Week Design Rules
status: active
confidence: 0.8
claim_label: fact
source_refs: [source-overview#chunk-001]
related_pages: []
---
# Curriculum Week Design Rules
\"\"\",
        encoding="utf-8",
    )

    subprocess.run([sys.executable, str(REBUILD_SCRIPT), str(repo)], check=True)

    index_text = (repo / "kb" / "index.md").read_text(encoding="utf-8")
    gap_report_text = (repo / "generated" / "reports" / "gap-report.md").read_text(encoding="utf-8")

    assert "24-Week Theme Map" not in index_text
    assert "24-Week Theme Map" not in gap_report_text
    assert "Curriculum Week Design Rules" in index_text
```

- [ ] **Step 4: Run the targeted tests to verify they fail for the right reason**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q -k "week_maps or fail_when_generated_week_maps_are_missing"
pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q -k deleted_curriculum_week_maps
```

Expected:
- FAIL because the current generator still reads `kb/curriculum/*-theme-map.md`
- FAIL because no generated `week-maps/` artifacts are produced yet

- [ ] **Step 5: Commit the test-first boundary changes**

```bash
git add tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py
git commit -m "test: lock curriculum week maps to generated outputs"
```

### Task 2: Add Generated Week-Map Loading And Two-Stage Generator Plumbing

**Files:**
- Modify: `repo_generators/curriculum.py`
- Modify: `jobs/kin-bjj-weekly-curriculum/job.yaml`
- Reference: `skills/llm-knowledge-base/scripts/run_generation.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py`

- [ ] **Step 1: Add week-map path configuration that points to generated artifacts instead of KB pages**

```python
PROGRAM_CONFIG = {
    "youth": {
        "generated_week_map_path": "generated/{job_name}/week-maps/youth-24-week-theme-map.md",
        "program_title": "Youth",
        "class_length": "60 minutes",
    },
    "adult": {
        "generated_week_map_path": "generated/{job_name}/week-maps/adult-24-week-theme-map.md",
        "program_title": "Adult",
        "class_length": "60 minutes",
    },
    "tots": {
        "generated_week_map_path": "generated/{job_name}/week-maps/tots-12-week-theme-map.md",
        "program_title": "Tots",
        "class_length": "30 minutes",
    },
}
```

- [ ] **Step 2: Add helpers to write and load generated week-map artifacts**

```python
def generated_week_map_path(repo_root: Path, job_name: str, program: str) -> Path:
    template = PROGRAM_CONFIG[program]["generated_week_map_path"]
    return repo_root / template.format(job_name=job_name)


def render_generated_week_map(program: str, source_kb_pages: list[str], weeks: list[dict], warnings: list[str]) -> str:
    title = f"{PROGRAM_CONFIG[program]['program_title']} {'24' if program != 'tots' else '12'}-Week Theme Map"
    payload = json.dumps({"weeks": weeks}, indent=2)
    frontmatter = [
        "---",
        f"id: generated-{program}-week-map",
        "type: generated-curriculum-candidate",
        f'title: "{title}"',
        "status: active",
        "confidence: 0.65",
        "source_kb_pages:",
        *[f"  - {path}" for path in source_kb_pages],
        "generation_notes:",
        '  - "Synthesized from KB framework pages for deterministic curriculum rendering."',
        "warnings:",
        *[f'  - "{warning}"' for warning in warnings] if warnings else ['  - "No additional warnings."'],
        "---",
        f"# {title}",
        "",
        "## Structured Week Data",
        "",
        "```json",
        payload,
        "```",
        "",
    ]
    return "\n".join(frontmatter)
```

- [ ] **Step 3: Refactor program loading into Stage 1 synthesize and Stage 2 load functions**

```python
def synthesize_program_weeks(repo_root: Path, program: str, job_context: dict) -> tuple[dict, list[dict], list[str]]:
    metadata, weeks = load_program_data_from_kb_framework(repo_root, program)
    warnings: list[str] = []
    if program in {"adult", "youth"}:
        warnings.append("Week sequencing is synthesized from framework KB pages and may need manual refinement.")
    return metadata, weeks, warnings


def load_generated_program_data(repo_root: Path, job_name: str, program: str) -> tuple[dict, list[dict]]:
    path = generated_week_map_path(repo_root, job_name, program)
    if not path.exists():
        raise ValueError(f"missing generated week map: {path}")
    metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    return metadata, extract_json_block(body).get("weeks", [])
```

- [ ] **Step 4: Update `generate()` to write week maps first, then render curriculum from them**

```python
week_map_root = reset_output_dir(output_root / "week-maps")

for program in PROGRAM_CONFIG:
    source_metadata, weeks, warnings = synthesize_program_weeks(repo_root, program, job_context)
    week_map_path = generated_week_map_path(repo_root, job_name, program)
    ensure_dir(week_map_path.parent)
    write_text(
        week_map_path,
        render_generated_week_map(program, job_spec["inputs"].get("kb_pages", []), weeks, warnings),
        overwrite=True,
    )
    output_paths.append(week_map_path.relative_to(repo_root).as_posix())

for program in PROGRAM_CONFIG:
    metadata, weeks = load_generated_program_data(repo_root, job_name, program)
    output_dir = ensure_dir(curriculum_root / program)
    for week in weeks:
        ...
```

- [ ] **Step 5: Update the job file so KB inputs are framework pages, not week-map pages**

```yaml
inputs:
  kb_pages:
    - kb/curriculum/youth-24-week-curriculum-framework.md
    - kb/curriculum/curriculum-week-design-rules.md
    - kb/curriculum/groundwork-cycle-framework.md
    - kb/curriculum/takedown-framework.md
    - kb/curriculum/youth-submission-safety-framework.md
    - kb/curriculum/ibjjf-leg-lock-curriculum.md
  examples:
    fully-scripted-session:
      - jobs/kin-bjj-weekly-curriculum/examples/fully-scripted-session/week-01-offensive-cycle.md
```

- [ ] **Step 6: Run focused generator tests**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q
```

Expected:
- PASS for the new week-map path tests
- Any remaining failures should now be about week content assumptions, not file locations

- [ ] **Step 7: Commit the two-stage generator plumbing**

```bash
git add repo_generators/curriculum.py jobs/kin-bjj-weekly-curriculum/job.yaml tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py
git commit -m "feat: generate curriculum week maps under generated outputs"
```

### Task 3: Remove KB Week-Map Pages And Rebuild Indexes

**Files:**
- Delete: `kb/curriculum/adult-24-week-theme-map.md`
- Delete: `kb/curriculum/youth-24-week-theme-map.md`
- Delete: `kb/curriculum/tots-12-week-theme-map.md`
- Modify: `kb/index.md`
- Modify: `generated/reports/gap-report.md`
- Modify: `generated/reports/conflict-report.md`
- Modify: `generated/reports/improvement-report.md`
- Modify: `.kb-state/link-map.json`
- Test: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`

- [ ] **Step 1: Delete only the three week-map pages from `kb/curriculum/`**

```text
kb/curriculum/adult-24-week-theme-map.md
kb/curriculum/youth-24-week-theme-map.md
kb/curriculum/tots-12-week-theme-map.md
```

- [ ] **Step 2: Rebuild indexes and reports**

Run:

```bash
python3 skills/llm-knowledge-base/scripts/rebuild_indexes.py .
```

Expected:
- `kb/index.md` no longer lists the deleted week-map pages
- generated reports no longer link to those deleted KB pages
- `.kb-state/link-map.json` no longer contains those page ids

- [ ] **Step 3: Add an assertion that deleted page ids are absent from the rebuilt link map**

```python
link_map = json.loads((repo / ".kb-state" / "link-map.json").read_text(encoding="utf-8"))
assert "adult-24-week-theme-map" not in link_map
assert "youth-24-week-theme-map" not in link_map
assert "tots-12-week-theme-map" not in link_map
```

- [ ] **Step 4: Run the index rebuild tests**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q
```

Expected:
- PASS

- [ ] **Step 5: Commit the KB cleanup**

```bash
git add kb/index.md generated/reports/gap-report.md generated/reports/conflict-report.md generated/reports/improvement-report.md .kb-state/link-map.json tests/skills/llm_knowledge_base/test_rebuild_indexes.py
git rm kb/curriculum/adult-24-week-theme-map.md kb/curriculum/youth-24-week-theme-map.md kb/curriculum/tots-12-week-theme-map.md
git commit -m "refactor: keep curriculum week maps out of the knowledge base"
```

### Task 4: Regenerate The Job And Verify Deterministic Downstream Outputs

**Files:**
- Modify: `generated/kin-bjj-weekly-curriculum/week-maps/adult-24-week-theme-map.md`
- Modify: `generated/kin-bjj-weekly-curriculum/week-maps/youth-24-week-theme-map.md`
- Modify: `generated/kin-bjj-weekly-curriculum/week-maps/tots-12-week-theme-map.md`
- Modify: `generated/kin-bjj-weekly-curriculum/curriculum/**`
- Modify: `generated/kin-bjj-weekly-curriculum/_meta/run.json`
- Reference: `jobs/kin-bjj-weekly-curriculum/examples/fully-scripted-session/week-01-offensive-cycle.md`
- Reference: `jobs/kin-bjj-weekly-curriculum/notes.md`

- [ ] **Step 1: Run the curriculum generation job end to end**

Run:

```bash
python3 skills/llm-knowledge-base/scripts/run_generation.py . --job-name kin-bjj-weekly-curriculum
```

Expected:
- generated week maps appear under `generated/kin-bjj-weekly-curriculum/week-maps/`
- downstream curriculum files regenerate successfully
- no files are written back into `kb/`

- [ ] **Step 2: Inspect one generated week map and one downstream file per program**

Run:

```bash
sed -n '1,120p' generated/kin-bjj-weekly-curriculum/week-maps/adult-24-week-theme-map.md
sed -n '1,120p' generated/kin-bjj-weekly-curriculum/week-maps/youth-24-week-theme-map.md
sed -n '1,120p' generated/kin-bjj-weekly-curriculum/week-maps/tots-12-week-theme-map.md
sed -n '1,120p' generated/kin-bjj-weekly-curriculum/curriculum/adult/week-01-fully-scripted-session.md
sed -n '1,120p' generated/kin-bjj-weekly-curriculum/curriculum/youth/week-01-curriculum.md
sed -n '1,120p' generated/kin-bjj-weekly-curriculum/curriculum/tots/week-01-curriculum.md
```

Expected:
- week maps include frontmatter plus a JSON `weeks` payload
- curriculum files still render deterministically from structured week data
- fully scripted sessions still honor the configured example style

- [ ] **Step 3: Run the full relevant test suite**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q
pytest tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q
pytest tests/skills/llm_knowledge_base/test_run_generation.py -q
```

Expected:
- PASS

- [ ] **Step 4: Check the final diff shape**

Run:

```bash
git status --short
```

Expected:
- deleted KB week-map pages
- generator, job config, and test updates
- regenerated files under `generated/kin-bjj-weekly-curriculum/`
- no unexpected changes under `raw/`

- [ ] **Step 5: Commit the regenerated output set**

```bash
git add generated/kin-bjj-weekly-curriculum repo_generators/curriculum.py jobs/kin-bjj-weekly-curriculum/job.yaml tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py
git commit -m "feat: generate curriculum artifacts from generated week maps"
```

## Self-Review

- Spec coverage:
  - Delete the three KB week-map pages: covered by Task 3.
  - Rebuild indexes and remove references: covered by Task 3.
  - Generate candidate week maps under `generated/.../week-maps/`: covered by Task 2 and Task 4.
  - Deterministically render curriculum files from generated week maps only: covered by Task 2 and Task 4.
  - No fallback to KB week maps: covered by Task 1 and Task 2.
  - Surface warnings/gaps when synthesis is inferred: covered by Task 2.
- Placeholder scan:
  - No `TODO`, `TBD`, or “implement later” placeholders remain.
- Type consistency:
  - The plan consistently uses `generated-curriculum-candidate`, `generated week map`, `weeks`, and `generated/.../week-maps/` across all tasks.
