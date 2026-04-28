import subprocess
import sys
from pathlib import Path

INIT_SCRIPT = Path("skills/llm-knowledge-base/scripts/init_repo.py").resolve()
RUN_SCRIPT = Path("skills/llm-knowledge-base/scripts/run_generation.py").resolve()
LEGACY_SCRIPT = Path("skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py").resolve()

FRAMEWORK_INPUTS = [
    "kb/curriculum/curriculum-week-design-rules.md",
    "kb/curriculum/youth-24-week-curriculum-framework.md",
    "kb/curriculum/adult-24-week-curriculum-framework.md",
    "kb/curriculum/tots-12-week-curriculum-framework.md",
    "kb/curriculum/groundwork-cycle-framework.md",
    "kb/curriculum/takedown-framework.md",
    "kb/curriculum/takedown-progression-framework.md",
    "kb/curriculum/youth-submission-safety-framework.md",
    "kb/curriculum/ibjjf-leg-lock-curriculum.md",
    "kb/concepts/movement-and-warmup-framework.md",
    "kb/concepts/general-physical-preparedness-framework.md",
]


def write_page(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_framework_page(repo: Path, relative_path: str, page_id: str, title: str, body: str) -> None:
    write_page(
        repo / relative_path,
        f"""---
id: {page_id}
type: curriculum-unit
title: "{title}"
status: active
confidence: 0.8
claim_label: editorial-normalization
source_refs:
  - source-overview#chunk-001
related_pages: []
---
# {title}

{body}
""",
    )


def seed_repo_with_sources_and_theme_maps(repo: Path) -> None:
    write_page(
        repo / "kb" / "sources" / "overview.md",
        """---
id: source-overview
type: source
title: "Overview"
status: active
confidence: 1.0
source_refs: []
related_pages: []
---
# Overview
""",
    )
    write_page(
        repo / "kb" / "sources" / "compendium.md",
        """---
id: source-compendium
type: source
title: "Compendium"
status: active
confidence: 1.0
source_refs: []
related_pages: []
---
# Compendium
""",
    )

    write_framework_page(
        repo,
        "kb/curriculum/curriculum-week-design-rules.md",
        "curriculum-week-design-rules",
        "Curriculum Week Design Rules",
        "Weekly curriculum design follows a fixed set of rules intended to keep theme, progression, and coach usability aligned.",
    )
    write_framework_page(
        repo,
        "kb/curriculum/youth-24-week-curriculum-framework.md",
        "youth-24-week-curriculum-framework",
        "Youth 24-Week Curriculum Framework",
        "The youth framework defines a 24-week sequence. Each weekly curriculum includes both a takedown component and a ground component.",
    )
    write_framework_page(
        repo,
        "kb/curriculum/adult-24-week-curriculum-framework.md",
        "adult-24-week-curriculum-framework",
        "Adult 24-Week Curriculum Framework",
        "The adult framework defines a 24-week sequence. Each weekly curriculum includes both a takedown component and a ground component.",
    )
    write_framework_page(
        repo,
        "kb/curriculum/tots-12-week-curriculum-framework.md",
        "tots-12-week-curriculum-framework",
        "Tots 12-Week Curriculum Framework",
        "The tots framework defines a 12-week movement-led sequence for shorter classes.",
    )
    write_framework_page(
        repo,
        "kb/curriculum/groundwork-cycle-framework.md",
        "groundwork-cycle-framework",
        "Groundwork Cycle Framework",
        "Groundwork themes should progress through connected exchanges.",
    )
    write_framework_page(
        repo,
        "kb/curriculum/takedown-framework.md",
        "takedown-framework",
        "Takedown Framework",
        "Weekly classes should include standing work and takedown development.",
    )
    write_framework_page(
        repo,
        "kb/curriculum/takedown-progression-framework.md",
        "takedown-progression-framework",
        "Takedown Progression Framework",
        "Standing skills should scale from basic entries into reactions and chains.",
    )
    write_framework_page(
        repo,
        "kb/curriculum/youth-submission-safety-framework.md",
        "youth-submission-safety-framework",
        "Youth Submission Safety Framework",
        "Youth submission teaching should emphasize safe pacing and control.",
    )
    write_framework_page(
        repo,
        "kb/curriculum/ibjjf-leg-lock-curriculum.md",
        "ibjjf-leg-lock-curriculum",
        "IBJJF Leg Lock Curriculum",
        "Adult lower-body work should stay rules-aware and safety-aware.",
    )
    write_framework_page(
        repo,
        "kb/concepts/movement-and-warmup-framework.md",
        "movement-and-warmup-framework",
        "Movement and Warmup Framework",
        "Movement training supplies the warm-up and body-awareness structure for beginner classes.",
    )
    write_framework_page(
        repo,
        "kb/concepts/general-physical-preparedness-framework.md",
        "general-physical-preparedness-framework",
        "General Physical Preparedness Framework",
        "Foundational movement for younger students should prioritize balance, coordination, and safe body control.",
    )


def seed_repo_reports(repo: Path) -> None:
    write_page(repo / "generated" / "reports" / "gap-report.md", "# Gap Report\n")
    write_page(repo / "generated" / "reports" / "conflict-report.md", "# Conflict Report\n")
    write_page(repo / "generated" / "reports" / "improvement-report.md", "# Improvement Report\n")


def write_job_yaml(repo: Path, job_name: str, *, generator: str = "curriculum") -> None:
    write_page(
        repo / "jobs" / job_name / "job.yaml",
        f"""id: {job_name}
title: Test Job {job_name}
generator: {generator}
generation_targets:
  - curriculum
status: active
transient: false
inputs:
  kb_pages:
{chr(10).join(f"    - {path}" for path in FRAMEWORK_INPUTS)}
options:
  include_reports: true
  emit_new_facts: true
""",
    )
    write_page(
        repo / "jobs" / job_name / "notes.md",
        """# Notes

## Purpose

Generate curriculum outputs for testing.

## Instructions

- Use the framework KB pages.

## Q&A

- No additional Q&A.

## Notes

No extra notes.
""",
    )


def test_run_generation_executes_curriculum_job_from_job_yaml(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_yaml(repo, "weekly-curriculum")

    result = subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (repo / "generated" / "weekly-curriculum" / "_meta" / "run.json").exists()


def test_run_generation_rejects_unknown_generator(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_yaml(repo, "weekly-curriculum", generator="unknown")

    result = subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "unknown generator" in result.stderr


def test_legacy_curriculum_script_delegates_to_generic_runner(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_yaml(repo, "weekly-curriculum")

    result = subprocess.run(
        [sys.executable, str(LEGACY_SCRIPT), str(repo), "--job-name", "weekly-curriculum"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (repo / "generated" / "weekly-curriculum" / "_meta" / "run.json").exists()
