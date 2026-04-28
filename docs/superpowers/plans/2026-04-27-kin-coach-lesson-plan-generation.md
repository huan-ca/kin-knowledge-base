# KIN Coach Lesson Plan Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a new job-scoped generator that creates coach-facing adult, youth, and tots lesson plans plus separate KB-grounding and missing-information files from current `kb/` evidence and deterministic synthesis rules.

**Architecture:** Add a separate `coach_lesson_plans` generator module under `repo_generators/`, register it in the shared generator registry, and drive it through the existing `run_generation.py` runner with a new job under `jobs/kin-bjj-coach-lesson-plans/`. The generator will load example-format KB pages, synthesize deterministic weekly records in memory, render coach-facing files under `generated/<job>/lesson/`, and render provenance/gap files under `generated/<job>/meta/`.

**Tech Stack:** Python 3, repo-local generator registry, markdown frontmatter parsing helpers in `common.py`, pytest

---

### Task 1: Add the new generator contract and failing integration tests

**Files:**
- Create: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`
- Modify: `tests/skills/llm_knowledge_base/test_run_generation.py`
- Create: `jobs/kin-bjj-coach-lesson-plans/job.yaml`
- Create: `jobs/kin-bjj-coach-lesson-plans/notes.md`

- [ ] **Step 1: Write the new integration-style output test file**

```python
import subprocess
import sys
from pathlib import Path

INIT_SCRIPT = Path("skills/llm-knowledge-base/scripts/init_repo.py").resolve()
RUN_SCRIPT = Path("skills/llm-knowledge-base/scripts/run_generation.py").resolve()


def write_page(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def seed_example_kb(repo: Path) -> None:
    write_page(
        repo / "kb" / "sources" / "high-level-overview.md",
        \"\"\"---
id: source-high-level-overview
type: source
title: "High Level Overview"
status: active
confidence: 0.8
claim_label: fact
source_refs: []
related_pages: []
---
# High Level Overview

## Extracted Notes
- Adult and youth run 24-week programs.
- Tots runs a 12-week movement-based program.
\"\"\",
    )
    write_page(
        repo / "kb" / "lessons" / "double-leg-side-control-americana-example-lesson.md",
        \"\"\"---
id: double-leg-side-control-americana-example-lesson
type: lesson
title: "Double Leg to Side Control to Americana Example Lesson"
status: active
confidence: 0.6
claim_label: editorial-normalization
source_refs:
  - source-example-scripted-lesson-plan-adult#chunk-001
related_pages: []
---
# Double Leg to Side Control to Americana Example Lesson

## Preserved Example Format

````markdown
## Week 1 (Offensive Cycle)
- Theme: Double Leg to Side Control to Americana
- Teaching Goal: Build one connected offensive sequence.

## Opening Script
Introduce the theme.

## Warm-Up Options
- Duck walks
- Breakfalls

## Lesson
- **Takedown**
  - Level 1: Double leg
- **Ground**
  - Level 1: Side control control

## Closing Script
Recap the lesson.
````
\"\"\",
    )
    write_page(
        repo / "kb" / "lessons" / "tots-week-1-mat-rules-base-ready-stance-example.md",
        \"\"\"---
id: tots-week-1-mat-rules-base-ready-stance-example
type: lesson
title: "Tots Week 1 Mat Rules, Base, And Ready Stance Example"
status: active
confidence: 0.8
claim_label: fact
source_refs:
  - source-example-scripted-lesson-plan-tots#chunk-001
related_pages: []
---
# Tots Week 1 Mat Rules, Base, And Ready Stance Example

## Preserved Example Format

````markdown
## Week 1 (Foundation)
Theme: Mat Rules, Base, And Ready Stance

## Lesson
### Warm-Up Block
- Bear crawls

### Main Activity Block
- Red light green light

### Closing Script
- Recap the theme
````
\"\"\",
    )


def write_job(repo: Path) -> None:
    write_page(
        repo / "jobs" / "coach-job" / "job.yaml",
        \"\"\"id: coach-job
title: Test Coach Lesson Plans
generator: coach_lesson_plans
generation_targets:
  - lesson-plan
status: active
transient: false
inputs:
  kb_pages:
    - kb/lessons/double-leg-side-control-americana-example-lesson.md
    - kb/lessons/tots-week-1-mat-rules-base-ready-stance-example.md
options:
  include_reports: false
  emit_missing_info_files: true
\"\"\",
    )
    write_page(
        repo / "jobs" / "coach-job" / "notes.md",
        \"\"\"# Notes

## Purpose

Generate coach-facing lesson plans.

## Instructions

- Preserve example-style formatting.
- Keep lesson files coach-facing.

## Q&A

- Adult and youth are 24 weeks.
- Tots is 12 weeks.

## Notes

No extra notes.
\"\"\",
    )


def test_generate_coach_lesson_plans_creates_root_syllabi_and_program_week_files(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_example_kb(repo)
    write_job(repo)

    result = subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "coach-job"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (repo / "generated" / "coach-job" / "lesson" / "adult-syllabus.md").exists()
    assert (repo / "generated" / "coach-job" / "lesson" / "adult" / "week-01-lesson-plan.md").exists()
    assert (repo / "generated" / "coach-job" / "meta" / "adult" / "week-01-kb-grounding.md").exists()
```

- [ ] **Step 2: Extend the new test file with explicit format and separation assertions**

```python
def test_generate_coach_lesson_plans_keep_provenance_out_of_lesson_files(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_example_kb(repo)
    write_job(repo)

    subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "coach-job"],
        capture_output=True,
        text=True,
        check=True,
    )

    lesson_text = (repo / "generated" / "coach-job" / "lesson" / "adult" / "week-01-lesson-plan.md").read_text(encoding="utf-8")
    grounding_text = (repo / "generated" / "coach-job" / "meta" / "adult" / "week-01-kb-grounding.md").read_text(encoding="utf-8")

    assert "## Opening Script" in lesson_text
    assert "## Warm-Up Options" in lesson_text
    assert "source_refs" not in lesson_text
    assert "claim_label" not in lesson_text
    assert "## KB-Grounded Inputs" in grounding_text
    assert "## Inferred Content" in grounding_text
```

- [ ] **Step 3: Extend the output test file for deterministic reset behavior and tots shape**

```python
def test_generate_coach_lesson_plans_resets_output_tree_and_renders_tots_style(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_example_kb(repo)
    write_job(repo)

    output_root = repo / "generated" / "coach-job"
    stale_file = output_root / "lesson" / "adult" / "stale.md"
    stale_file.parent.mkdir(parents=True, exist_ok=True)
    stale_file.write_text("stale", encoding="utf-8")

    subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "coach-job"],
        capture_output=True,
        text=True,
        check=True,
    )

    tots_text = (output_root / "lesson" / "tots" / "week-01-lesson-plan.md").read_text(encoding="utf-8")

    assert not stale_file.exists()
    assert "### Main Activity Block" in tots_text
    assert "### Intro Grappling Block" in tots_text
```

- [ ] **Step 4: Update the runner test to prove the new generator id works**

```python
def test_run_generation_executes_coach_lesson_plan_job_from_job_yaml(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_example_kb(repo)
    write_job(repo)

    result = subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "coach-job"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (repo / "generated" / "coach-job" / "_meta" / "run.json").exists()
```

- [ ] **Step 5: Add the real job inputs under `jobs/kin-bjj-coach-lesson-plans/`**

```yaml
# jobs/kin-bjj-coach-lesson-plans/job.yaml
id: kin-bjj-coach-lesson-plans
title: KIN BJJ Coach Lesson Plans
generator: coach_lesson_plans
generation_targets:
  - lesson-plan
status: active
transient: false
inputs:
  kb_pages:
    - kb/sources/high-level-overview.md
    - kb/sources/kin-bjj-compendium.md
    - kb/sources/kin-bjj-kids-lesson-plan-structure.md
    - kb/lessons/double-leg-side-control-americana-example-lesson.md
    - kb/lessons/tots-week-1-mat-rules-base-ready-stance-example.md
    - kb/concepts/four-layers-of-bjj-skill-development.md
  examples: {}
options:
  include_reports: true
  emit_missing_info_files: true
```

```markdown
# jobs/kin-bjj-coach-lesson-plans/notes.md

## Purpose

Generate final coach-facing lesson plans and syllabi for adult, youth, and tots.

## Instructions

- Preserve the example lesson format.
- Prefer list-heavy formatting over prose-heavy formatting.
- Keep coach notes inside the lesson-plan file.
- Put provenance and missing-information details under `meta/`.

## Q&A

- Adult and youth are 24 weeks.
- Adults use leg-lock framing where youth uses self-defence framing.
- Tots is 12 weeks and movement/game led.

## Notes

Use deterministic synthesis and make unsupported decisions explicit in `meta/`.
```

- [ ] **Step 6: Run the focused failing tests**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py tests/skills/llm_knowledge_base/test_run_generation.py -q`

Expected: FAIL with `unknown generator: coach_lesson_plans` and missing output assertions.

- [ ] **Step 7: Commit the red test state**

```bash
git add tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py tests/skills/llm_knowledge_base/test_run_generation.py jobs/kin-bjj-coach-lesson-plans/job.yaml jobs/kin-bjj-coach-lesson-plans/notes.md
git commit -m "test: add coach lesson plan generation coverage"
```

### Task 2: Implement KB loading and deterministic weekly synthesis

**Files:**
- Create: `repo_generators/coach_lesson_plans.py`
- Modify: `repo_generators/registry.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`

- [ ] **Step 1: Add the generator module with config, reset logic, and KB page loading helpers**

```python
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from common import ensure_dir, parse_frontmatter, write_text


PROGRAM_RULES = {
    "adult": {"weeks": 24, "class_length": "60 minutes"},
    "youth": {"weeks": 24, "class_length": "60 minutes"},
    "tots": {"weeks": 12, "class_length": "30 minutes"},
}


@dataclass(frozen=True)
class ExampleFormat:
    title: str
    body: str
    sections: tuple[str, ...]


def reset_output_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    return ensure_dir(path)


def load_markdown_page(path: Path) -> tuple[dict, str]:
    metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    return metadata, body


def extract_preserved_example(body: str) -> str:
    marker = "## Preserved Example Format"
    if marker not in body:
        raise ValueError("missing preserved example format section")
    return body.split(marker, 1)[1].strip()
```

- [ ] **Step 2: Register the new generator id**

```python
GENERATOR_REGISTRY = {
    "curriculum": "repo_generators.curriculum",
    "coach_lesson_plans": "repo_generators.coach_lesson_plans",
}
```

- [ ] **Step 3: Add deterministic week synthesis structures for adult, youth, and tots**

```python
def build_cycle_label(week: int) -> str:
    return "offensive" if ((week - 1) // 2) % 2 == 0 else "defensive"


def synthesize_adult_week(week: int) -> dict:
    lower_body = week in (23, 24)
    return {
        "week": week,
        "program": "adult",
        "cycle": build_cycle_label(week),
        "theme": "Lower-Body Control and Safety" if lower_body else f"Adult Fundamentals Week {week:02d}",
        "teaching_goal": "Build connected takedown-to-ground fundamentals." if not lower_body else "Introduce lower-body control with clear safety constraints.",
        "coach_notes": [
            "Keep explanations compact and action-first.",
            "Reinforce safe pacing during partner work.",
        ],
        "content_basis": "adult_leg_lock" if lower_body else "adult_foundations",
    }


def synthesize_youth_week(week: int) -> dict:
    self_defence = week in (23, 24)
    return {
        "week": week,
        "program": "youth",
        "cycle": build_cycle_label(week),
        "theme": "Self-Defence Awareness" if self_defence else f"Youth Fundamentals Week {week:02d}",
        "teaching_goal": "Build connected takedown-to-ground fundamentals." if not self_defence else "Frame safe self-defence responses with clear boundaries.",
        "coach_notes": [
            "Use short cues and keep transitions organized.",
            "Frame self-defence work as awareness and posture, not escalation.",
        ],
        "content_basis": "youth_self_defence" if self_defence else "youth_foundations",
    }


def synthesize_tots_week(week: int) -> dict:
    return {
        "week": week,
        "program": "tots",
        "cycle": "foundation" if week <= 4 else "movement" if week <= 8 else "partner",
        "theme": f"Tots Movement Week {week:02d}",
        "teaching_goal": "Build balance, listening, and playful mat confidence.",
        "coach_notes": [
            "Keep the room moving quickly.",
            "Use praise and short resets.",
        ],
        "content_basis": "tots_movement",
    }
```

- [ ] **Step 4: Add a single synthesis entry point that validates example KB inputs**

```python
def synthesize_program_weeks(job_spec: dict, kb_pages: dict[str, tuple[dict, str]]) -> dict[str, list[dict]]:
    if "adult_example" not in kb_pages or "tots_example" not in kb_pages:
        raise ValueError("coach lesson plan generation requires adult/youth and tots example KB pages")

    return {
        "adult": [synthesize_adult_week(week) for week in range(1, 25)],
        "youth": [synthesize_youth_week(week) for week in range(1, 25)],
        "tots": [synthesize_tots_week(week) for week in range(1, 13)],
    }
```

- [ ] **Step 5: Run the targeted tests**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py tests/skills/llm_knowledge_base/test_run_generation.py -q`

Expected: FAIL on missing rendered files, but no longer fail with `unknown generator`.

- [ ] **Step 6: Commit the synthesis scaffold**

```bash
git add repo_generators/coach_lesson_plans.py repo_generators/registry.py
git commit -m "feat: scaffold coach lesson plan generator"
```

### Task 3: Render coach-facing lesson files, syllabi, and meta files

**Files:**
- Modify: `repo_generators/coach_lesson_plans.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`

- [ ] **Step 1: Add syllabus rendering under `lesson/`**

```python
def render_syllabus(program: str, weeks: list[dict]) -> str:
    lines = [
        f"# {program.title()} Syllabus",
        "",
        f"- Total Weeks: {len(weeks)}",
        f"- Class Length: {PROGRAM_RULES[program]['class_length']}",
        "",
        "## Weekly Themes",
    ]
    for week in weeks:
        lines.append(f"- Week {week['week']:02d}: {week['theme']} - {week['teaching_goal']}")
    lines.append("")
    return "\n".join(lines)
```

- [ ] **Step 2: Add list-heavy coach lesson rendering that keeps provenance out**

```python
def render_adult_or_youth_lesson(week: dict) -> str:
    return "\n".join(
        [
            f"# Week {week['week']:02d} Lesson Plan",
            "",
            f"- Program: {week['program'].title()}",
            f"- Cycle: {week['cycle'].title()}",
            f"- Theme: {week['theme']}",
            f"- Teaching Goal: {week['teaching_goal']}",
            f"- Class Length: {PROGRAM_RULES[week['program']]['class_length']}",
            "",
            "## Opening Script",
            f"- Today we are working on {week['theme'].lower()}.",
            "",
            "## Warm-Up Options",
            "- Movement prep tied to stance, level change, and mat awareness.",
            "- Partner entry reps with light pacing.",
            "",
            "## Lesson",
            "- **Takedown Block**",
            "  - Level 1: Entry and posture.",
            "  - Level 2: Finish to controlled top position.",
            "- **Ground Block**",
            "  - Level 1: Secure control and stabilize.",
            "  - Level 2: Advance to a simple finish or positional win condition.",
            "",
            "## Coach Notes",
            *[f"- {note}" for note in week["coach_notes"]],
            "",
            "## Situational Work",
            "- Start from the intended control point and rotate quickly.",
            "",
            "## Closing Script",
            "- Recap the main win condition and one safety reminder.",
            "",
        ]
    )


def render_tots_lesson(week: dict) -> str:
    return "\n".join(
        [
            f"# Week {week['week']:02d} Lesson Plan",
            "",
            f"- Program: Tots",
            f"- Cycle: {week['cycle'].title()}",
            f"- Theme: {week['theme']}",
            f"- Teaching Goal: {week['teaching_goal']}",
            f"- Class Length: {PROGRAM_RULES['tots']['class_length']}",
            "",
            "## Lesson",
            "### Introduce the Theme",
            f"- Tell the class the goal is {week['theme'].lower()}.",
            "",
            "### Warm-Up Block",
            "- Use a short movement game tied to balance and stopping on command.",
            "",
            "### Main Activity Block",
            "- Run one playful game with clear freeze and reset moments.",
            "",
            "### Intro Grappling Block",
            "- Expose the students to stance, posture, or personal-space habits.",
            "",
            "### Closing Script",
            "- Praise the room, recap one success, and dismiss clearly.",
            "",
        ]
    )
```

- [ ] **Step 3: Add meta renderers for KB grounding and fill-in-ready missing information**

```python
def render_kb_grounding(week: dict) -> str:
    return "\n".join(
        [
            f"# Week {week['week']:02d} KB Grounding",
            "",
            "## KB-Grounded Inputs",
            "- Example lesson structure came from preserved KB example pages.",
            "- Program length and broad audience split came from KB source pages.",
            "",
            "## Inferred Content",
            f"- Weekly sequencing for {week['program']} was synthesized deterministically.",
            f"- Theme wording for week {week['week']:02d} is generator-authored.",
            "",
            "## Weak Support",
            "- Exact week-by-week technique sequence is not fully source-authored in the KB.",
            "",
        ]
    )


def render_missing_info(week: dict) -> str:
    return "\n".join(
        [
            f"# Week {week['week']:02d} Missing Information",
            "",
            "## Human Decisions Needed",
            "- Preferred class length override: ____________________",
            "- Preferred competition vs fundamentals balance: ____________________",
            "- Program-specific emphasis adjustment: ____________________",
            "",
            "## Notes",
            "- Fill this only if you want to override the provisional generated plan.",
            "",
        ]
    )
```

- [ ] **Step 4: Add the `generate()` entry point that writes the output tree**

```python
def generate(repo_root: Path, job_spec: dict, job_context: dict) -> dict:
    output_root = reset_output_dir(repo_root / "generated" / job_context["job_name"])
    lesson_root = ensure_dir(output_root / "lesson")
    meta_root = ensure_dir(output_root / "meta")

    kb_pages = load_kb_inputs(repo_root, job_spec)
    program_weeks = synthesize_program_weeks(job_spec, kb_pages)
    outputs: list[str] = []

    for program, weeks in program_weeks.items():
        syllabus_path = lesson_root / f"{program}-syllabus.md"
        write_text(syllabus_path, render_syllabus(program, weeks), overwrite=True)
        outputs.append(syllabus_path.relative_to(repo_root).as_posix())

        for week in weeks:
            lesson_path = lesson_root / program / f"week-{week['week']:02d}-lesson-plan.md"
            grounding_path = meta_root / program / f"week-{week['week']:02d}-kb-grounding.md"
            missing_info_path = meta_root / program / f"week-{week['week']:02d}-missing-info.md"

            lesson_text = render_tots_lesson(week) if program == "tots" else render_adult_or_youth_lesson(week)
            write_text(lesson_path, lesson_text, overwrite=True)
            write_text(grounding_path, render_kb_grounding(week), overwrite=True)
            write_text(missing_info_path, render_missing_info(week), overwrite=True)

            outputs.extend(
                [
                    lesson_path.relative_to(repo_root).as_posix(),
                    grounding_path.relative_to(repo_root).as_posix(),
                    missing_info_path.relative_to(repo_root).as_posix(),
                ]
            )

    return {"outputs": outputs, "warnings": [], "new_facts_count": 0}
```

- [ ] **Step 5: Run the focused tests**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py tests/skills/llm_knowledge_base/test_run_generation.py -q`

Expected: PASS for the new coach-plan tests and the new run-generation coverage.

- [ ] **Step 6: Commit the renderer implementation**

```bash
git add repo_generators/coach_lesson_plans.py
git commit -m "feat: render coach lesson plan outputs"
```

### Task 4: Tighten validation, real-job behavior, and final verification

**Files:**
- Modify: `repo_generators/coach_lesson_plans.py`
- Modify: `jobs/kin-bjj-coach-lesson-plans/job.yaml`
- Modify: `jobs/kin-bjj-coach-lesson-plans/notes.md`
- Test: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`

- [ ] **Step 1: Add validation around required KB example inputs and deterministic counts**

```python
def validate_program_weeks(program_weeks: dict[str, list[dict]]) -> None:
    if len(program_weeks["adult"]) != 24:
        raise ValueError("adult coach lesson plans require 24 weeks")
    if len(program_weeks["youth"]) != 24:
        raise ValueError("youth coach lesson plans require 24 weeks")
    if len(program_weeks["tots"]) != 12:
        raise ValueError("tots coach lesson plans require 12 weeks")
```

- [ ] **Step 2: Add a failure-mode test for missing example-format KB pages**

```python
def test_generate_coach_lesson_plans_requires_example_kb_pages(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    write_job(repo)

    result = subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "coach-job"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "example KB pages" in result.stderr
```

- [ ] **Step 3: Update the real job notes and options if implementation details changed during coding**

```yaml
options:
  include_reports: true
  emit_missing_info_files: true
  emit_missing_info_placeholders_for_all_weeks: true
```

```markdown
## Notes

Use deterministic synthesis. Keep lesson files coach-facing and keep unsupported sequencing claims out of `lesson/`.
```

- [ ] **Step 4: Run the full targeted verification set**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py tests/skills/llm_knowledge_base/test_run_generation.py -q`

Expected: PASS

Run: `python3 -m py_compile repo_generators/coach_lesson_plans.py repo_generators/registry.py`

Expected: no output

Run: `python3 skills/llm-knowledge-base/scripts/run_generation.py . --job-name kin-bjj-coach-lesson-plans`

Expected: generates:
- `generated/kin-bjj-coach-lesson-plans/lesson/adult-syllabus.md`
- `generated/kin-bjj-coach-lesson-plans/lesson/adult/week-01-lesson-plan.md`
- `generated/kin-bjj-coach-lesson-plans/meta/adult/week-01-kb-grounding.md`
- matching youth and tots trees

- [ ] **Step 5: Inspect generated outputs manually**

Checklist:
- adult lesson file reads like a final coach document
- youth lesson file uses youth framing
- adult late weeks use lower-body framing
- youth late weeks use self-defence framing
- tots lesson file is game- and movement-led
- KB-grounding file clearly marks inferred content
- missing-information file is easy for a human to fill in

- [ ] **Step 6: Commit the validation and job wiring**

```bash
git add repo_generators/coach_lesson_plans.py jobs/kin-bjj-coach-lesson-plans/job.yaml jobs/kin-bjj-coach-lesson-plans/notes.md tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py tests/skills/llm_knowledge_base/test_run_generation.py
git commit -m "feat: finalize coach lesson plan job"
```
