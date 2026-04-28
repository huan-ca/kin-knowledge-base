import subprocess
import sys
from pathlib import Path

INIT_SCRIPT = Path("skills/llm-knowledge-base/scripts/init_repo.py").resolve()
RUN_SCRIPT = Path("skills/llm-knowledge-base/scripts/run_generation.py").resolve()
LEGACY_SCRIPT = Path("skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py").resolve()


def write_page(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_theme_map_page(
    repo: Path,
    *,
    relative_path: str,
    page_id: str,
    title: str,
    source_page_id: str,
    weeks_json: str,
) -> None:
    write_page(
        repo / relative_path,
        f"""---
id: {page_id}
type: curriculum-unit
title: "{title}"
status: active
confidence: 0.65
claim_label: editorial-normalization
source_refs:
  - {source_page_id}#chunk-001
related_pages: []
---
# {title}

## Structured Week Data

```json
{weeks_json}
```
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

    youth_weeks = """{
  "weeks": [
    {
      "week": 1,
      "theme": "Youth Theme 01",
      "cycle": "defensive",
      "teaching_goal": "Youth goal 01",
      "coach_notes": "Youth coach note 01",
      "sections": [
        {
          "name": "Ground Focus",
          "focus": "Youth ground focus 01",
          "level_1": "Youth level 1 option 01",
          "level_2": "Youth level 2 option 01",
          "coach_notes": "Youth section note 01"
        }
      ]
    }
  ]
}"""
    adult_weeks = """{
  "weeks": [
    {
      "week": 1,
      "theme": "Adult Theme 01",
      "cycle": "defensive",
      "teaching_goal": "Adult goal 01",
      "coach_notes": "Adult coach note 01",
      "adult_specific_notes": "Adult-specific note 01",
      "sections": [
        {
          "name": "Ground Focus",
          "focus": "Adult ground focus 01",
          "level_1": "Adult level 1 option 01",
          "level_2": "Adult level 2 option 01",
          "coach_notes": "Adult section note 01"
        }
      ]
    }
  ]
}"""
    tots_weeks = """{
  "weeks": [
    {
      "week": 1,
      "cycle": "foundation",
      "theme": "Tots Theme 01",
      "movement_theme": "Movement theme 01",
      "game": "Game 01",
      "coordination_focus": "Coordination focus 01",
      "bjj_exposure": "BJJ exposure 01",
      "coach_notes": "Tots coach note 01"
    }
  ]
}"""

    write_theme_map_page(
        repo,
        relative_path="kb/curriculum/youth-24-week-theme-map.md",
        page_id="youth-24-week-theme-map",
        title="Youth 24-Week Theme Map",
        source_page_id="source-overview",
        weeks_json=youth_weeks,
    )
    write_theme_map_page(
        repo,
        relative_path="kb/curriculum/adult-24-week-theme-map.md",
        page_id="adult-24-week-theme-map",
        title="Adult 24-Week Theme Map",
        source_page_id="source-overview",
        weeks_json=adult_weeks,
    )
    write_theme_map_page(
        repo,
        relative_path="kb/curriculum/tots-12-week-theme-map.md",
        page_id="tots-12-week-theme-map",
        title="Tots 12-Week Theme Map",
        source_page_id="source-compendium",
        weeks_json=tots_weeks,
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
    - kb/curriculum/youth-24-week-theme-map.md
    - kb/curriculum/adult-24-week-theme-map.md
    - kb/curriculum/tots-12-week-theme-map.md
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

- Use the KB week maps.

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
