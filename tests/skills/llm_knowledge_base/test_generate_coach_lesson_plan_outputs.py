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
        """---
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
""",
    )
    write_page(
        repo / "kb" / "lessons" / "double-leg-side-control-americana-example-lesson.md",
        """---
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
""",
    )
    write_page(
        repo / "kb" / "lessons" / "tots-week-1-mat-rules-base-ready-stance-example.md",
        """---
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
""",
    )


def write_job(repo: Path) -> None:
    write_page(
        repo / "jobs" / "coach-job" / "job.yaml",
        """id: coach-job
title: Test Coach Lesson Plans
generator: coach_lesson_plans
generation_targets:
  - lesson-plan
status: active
transient: false
inputs:
  kb_pages:
    - kb/sources/high-level-overview.md
    - kb/lessons/double-leg-side-control-americana-example-lesson.md
    - kb/lessons/tots-week-1-mat-rules-base-ready-stance-example.md
options:
  include_reports: false
  emit_missing_info_files: true
""",
    )
    write_page(
        repo / "jobs" / "coach-job" / "notes.md",
        """# Notes

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
""",
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
    assert (repo / "generated" / "coach-job" / "lesson" / "youth-syllabus.md").exists()
    assert (repo / "generated" / "coach-job" / "lesson" / "tots-syllabus.md").exists()
    assert (repo / "generated" / "coach-job" / "lesson" / "adult" / "week-01-lesson-plan.md").exists()
    assert (repo / "generated" / "coach-job" / "meta" / "adult" / "week-01-kb-grounding.md").exists()
    assert (repo / "generated" / "coach-job" / "meta" / "adult" / "week-01-missing-info.md").exists()


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

    lesson_text = (repo / "generated" / "coach-job" / "lesson" / "adult" / "week-01-lesson-plan.md").read_text(
        encoding="utf-8"
    )
    grounding_text = (repo / "generated" / "coach-job" / "meta" / "adult" / "week-01-kb-grounding.md").read_text(
        encoding="utf-8"
    )

    assert "## Opening Script" in lesson_text
    assert "## Warm-Up Options" in lesson_text
    assert "source_refs" not in lesson_text
    assert "claim_label" not in lesson_text
    assert "## KB-Grounded Inputs" in grounding_text
    assert "## Inferred Content" in grounding_text


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
