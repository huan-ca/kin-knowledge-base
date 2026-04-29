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
        repo / "kb" / "sources" / "kin-bjj-compendium.md",
        """---
id: source-kin-bjj-compendium
type: source
title: "KIN BJJ Compendium"
status: active
confidence: 1.0
source_refs: []
related_pages: []
---
# KIN BJJ Compendium

## Extracted Notes
- Guard, passing, escapes, and submission systems connect through positional control.
""",
    )
    write_page(
        repo / "kb" / "sources" / "kin-bjj-kids-lesson-plan-structure.md",
        """---
id: source-kin-bjj-kids-lesson-plan-structure
type: source
title: "KIN BJJ Kids Lesson Plan Structure"
status: active
confidence: 1.0
source_refs: []
related_pages: []
---
# KIN BJJ Kids Lesson Plan Structure

## Extracted Notes
- Keep explanations short.
- Use movement, drills, and games with quick transitions.
""",
    )
    write_page(
        repo / "kb" / "concepts" / "four-layers-of-bjj-skill-development.md",
        """---
id: four-layers-of-bjj-skill-development
type: concept
title: "Four Layers of BJJ Skill Development"
status: active
confidence: 0.9
claim_label: fact
source_refs:
  - source-high-level-overview#chunk-001
related_pages: []
---
# Four Layers of BJJ Skill Development

## Detailed Notes

- Techniques, repetition, principles, and intuition should be built in sequence.
""",
    )
    write_page(
        repo / "kb" / "concepts" / "escape-framework.md",
        """---
id: escape-framework
type: concept
title: "Escape Framework"
status: active
confidence: 0.88
claim_label: editorial-normalization
source_refs:
  - source-kin-bjj-compendium#chunk-escapes-001
related_pages: []
---
# Escape Framework

## Detailed Notes

- Frames before big bridge attempts keep the student calmer under pressure.
- Recover guard before chasing low-percentage reversals.

## Operational Implications

- Teach calm survival habits first.
""",
    )
    write_page(
        repo / "kb" / "concepts" / "movement-and-warmup-framework.md",
        """---
id: movement-and-warmup-framework
type: concept
title: "Movement and Warm-Up Framework"
status: active
confidence: 0.87
claim_label: fact
source_refs:
  - source-kin-bjj-kids-lesson-plan-structure#chunk-001
related_pages: []
---
# Movement and Warm-Up Framework

## Operational Implications

- Use movement warm-ups to reinforce posture, stance, and mat awareness.
- Keep warm-up explanations short and the room active.
""",
    )
    write_page(
        repo / "kb" / "concepts" / "submission-framework.md",
        """---
id: submission-framework
type: concept
title: "Submission Framework"
status: active
confidence: 0.86
claim_label: editorial-normalization
source_refs:
  - source-kin-bjj-compendium#chunk-submissions-001
related_pages: []
---
# Submission Framework

## Constraints or Safety Notes

- Teach finishing pressure gradually and expect early taps.
- Reinforce controlled tempo over speed.
""",
    )
    write_page(
        repo / "kb" / "position" / "guard-framework.md",
        """---
id: guard-framework
type: position
title: "Guard Framework"
status: active
confidence: 0.86
claim_label: editorial-normalization
source_refs:
  - source-kin-bjj-compendium#chunk-guard-001
related_pages: []
domain_tags: [guard, bottom-game]
keywords: [guard framework, guard retention, bottom position]
summary: Guard is treated as a bottom-position system built on retention, recovery, sweeping threats, and submission connections.
---
# Guard Framework

## Definition

Guard is the bottom-position framework for controlling distance, recovering structure, and launching reversals or attacks.

## Detailed Notes

- Guard work should begin with posture and connection before students chase speed.
- Recovery, retention, and immediate re-guarding are stronger teaching priorities than low-percentage scramble reactions.

## Operational Implications

- Coaches should cue structure before attack volume.
- Early weeks should reward calm guard recovery and connected follow-up.
""",
    )
    write_page(
        repo / "kb" / "position" / "side-control-system.md",
        """---
id: side-control-system
type: position
title: "Side Control System"
status: active
confidence: 0.85
claim_label: fact
source_refs:
  - source-kin-bjj-compendium#chunk-side-control-001
related_pages: []
---
# Side Control System

## Detailed Notes

- Win the head-and-shoulder line before hunting submissions.
""",
    )
    write_page(
        repo / "kb" / "class-types" / "class-structure-principles.md",
        """---
id: class-structure-principles
type: class-type
title: "Class Structure Principles"
status: active
confidence: 0.9
claim_label: fact
source_refs:
  - source-kin-bjj-kids-lesson-plan-structure#chunk-002
related_pages: []
---
# Class Structure Principles

## Operational Implications

- Keep the room moving with short explanation windows and clear reset points.
- Use firm structure without long lecture blocks.
""",
    )
    write_page(
        repo / "kb" / "class-types" / "competition-training-session-framework.md",
        """---
id: competition-training-session-framework
type: class-type
title: "Competition Training Session Framework"
status: active
confidence: 0.8
claim_label: editorial-normalization
source_refs:
  - source-high-level-overview#chunk-competition-001
related_pages: []
---
# Competition Training Session Framework

## Detailed Notes

- Build from movement to task-based rounds without wasting room time.
""",
    )
    write_page(
        repo / "kb" / "programs" / "kids-youth-development-program.md",
        """---
id: kids-youth-development-program
type: program
title: "Kids Youth Development Program"
status: active
confidence: 0.9
claim_label: fact
source_refs:
  - source-kin-bjj-kids-lesson-plan-structure#chunk-003
related_pages: []
---
# Kids Youth Development Program

## Operational Implications

- Use short cues, clear boundaries, and positive self-defence framing.
- Keep the room encouraging and values-oriented.
""",
    )
    write_page(
        repo / "kb" / "procedures" / "technical-lesson-delivery-model.md",
        """---
id: technical-lesson-delivery-model
type: procedure
title: "Technical Lesson Delivery Model"
status: active
confidence: 0.88
claim_label: fact
source_refs:
  - source-kin-bjj-kids-lesson-plan-structure#chunk-004
related_pages: []
---
# Technical Lesson Delivery Model

## Operational Implications

- Demonstrate briefly, then get partners moving quickly.
""",
    )
    write_page(
        repo / "kb" / "procedures" / "example-lesson-warmup-option-pattern.md",
        """---
id: example-lesson-warmup-option-pattern
type: procedure
title: "Example Lesson Warm-Up Option Pattern"
status: active
confidence: 0.84
claim_label: editorial-normalization
source_refs:
  - source-kin-bjj-kids-lesson-plan-structure#chunk-005
related_pages: []
---
# Example Lesson Warm-Up Option Pattern

## Detailed Notes

- Offer a movement-based and drill-based warm-up option.
""",
    )
    write_page(
        repo / "kb" / "procedures" / "example-situational-start-pattern.md",
        """---
id: example-situational-start-pattern
type: procedure
title: "Example Situational Start Pattern"
status: active
confidence: 0.84
claim_label: editorial-normalization
source_refs:
  - source-kin-bjj-kids-lesson-plan-structure#chunk-006
related_pages: []
---
# Example Situational Start Pattern

## Detailed Notes

- Start from the target control point and rotate on clear win conditions.
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
    - kb/sources/kin-bjj-compendium.md
    - kb/sources/kin-bjj-kids-lesson-plan-structure.md
    - kb/lessons/double-leg-side-control-americana-example-lesson.md
    - kb/lessons/tots-week-1-mat-rules-base-ready-stance-example.md
    - kb/concepts/four-layers-of-bjj-skill-development.md
    - kb/concepts/escape-framework.md
    - kb/concepts/movement-and-warmup-framework.md
    - kb/concepts/submission-framework.md
    - kb/position/guard-framework.md
    - kb/position/side-control-system.md
    - kb/class-types/class-structure-principles.md
    - kb/class-types/competition-training-session-framework.md
    - kb/procedures/technical-lesson-delivery-model.md
    - kb/procedures/example-lesson-warmup-option-pattern.md
    - kb/procedures/example-situational-start-pattern.md
    - kb/programs/kids-youth-development-program.md
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
    assert (repo / "generated" / "coach-job" / "meta" / "adult" / "missing-info.md").exists()
    assert not (repo / "generated" / "coach-job" / "meta" / "adult" / "week-01-missing-info.md").exists()


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
    missing_info_text = (repo / "generated" / "coach-job" / "meta" / "adult" / "missing-info.md").read_text(
        encoding="utf-8"
    )

    assert "## Opening Script" in lesson_text
    assert "## Warm-Up Options" in lesson_text
    assert "Submission / Win Condition" not in lesson_text
    assert "source_refs" not in lesson_text
    assert "claim_label" not in lesson_text
    assert "## KB-Grounded Inputs" in grounding_text
    assert "## Inferred Content" in grounding_text
    assert "# Adult Missing Information" in missing_info_text


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


def test_generate_coach_lesson_plans_archives_existing_output_tree(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_example_kb(repo)
    write_job(repo)

    current_root = repo / "generated" / "coach-job"
    archived_root = repo / "generated" / "coach-job-old"
    write_page(current_root / "lesson" / "adult" / "week-01-lesson-plan.md", "current output")
    write_page(archived_root / "stale.md", "stale archive")

    subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "coach-job"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert (archived_root / "lesson" / "adult" / "week-01-lesson-plan.md").exists()
    assert not (archived_root / "stale.md").exists()
    assert (current_root / "lesson" / "adult" / "week-01-lesson-plan.md").exists()


def test_generate_coach_lesson_plans_requires_example_kb_pages(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
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
""",
    )
    write_job(repo)

    result = subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "coach-job"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "example KB pages" in result.stderr


def test_generate_coach_lesson_plans_adult_syllabus_uses_table_format(tmp_path):
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

    syllabus_text = (repo / "generated" / "coach-job" / "lesson" / "adult-syllabus.md").read_text(encoding="utf-8")

    assert "| Week | Cycle | Theme | Main Goal |" in syllabus_text
    assert "| 01 | offensive |" in syllabus_text
    assert "- Program: Adult" not in syllabus_text
    assert "## Coach Note" not in syllabus_text


def test_generate_coach_lesson_plans_youth_and_tots_syllabi_use_same_table_format(tmp_path):
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

    youth_text = (repo / "generated" / "coach-job" / "lesson" / "youth-syllabus.md").read_text(encoding="utf-8")
    tots_text = (repo / "generated" / "coach-job" / "lesson" / "tots-syllabus.md").read_text(encoding="utf-8")

    assert "| Week | Cycle | Theme | Main Goal |" in youth_text
    assert "| Week | Cycle | Theme | Main Goal |" in tots_text
    assert "| 01 | offensive |" in youth_text
    assert "| 01 | foundation |" in tots_text


def test_generate_coach_lesson_plans_offensive_cycles_render_submission_block(tmp_path):
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

    assert "- **Submission:" in lesson_text
    assert "- **Situational Options**" in lesson_text
    assert "Coaching Emphasis:" in lesson_text
    assert "Safety:" in lesson_text


def test_generate_coach_lesson_plans_defensive_cycles_keep_situational_without_submission_block(tmp_path):
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

    lesson_text = (repo / "generated" / "coach-job" / "lesson" / "adult" / "week-03-lesson-plan.md").read_text(
        encoding="utf-8"
    )

    assert "- **Submission:" not in lesson_text
    assert "- **Situational Options**" in lesson_text
    assert (
        "Frames before big bridge attempts keep the student calmer under pressure." in lesson_text
        or "Recover guard before chasing low-percentage reversals." in lesson_text
    )
