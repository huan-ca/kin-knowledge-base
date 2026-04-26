import json
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

INIT_SCRIPT = Path("skills/llm-knowledge-base/scripts/init_repo.py").resolve()
GENERATE_SCRIPT = Path("skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py").resolve()


def write_page(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def hash_tree(root: Path) -> str:
    digest = sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def build_youth_weeks() -> list[dict]:
    weeks = []
    for week in range(1, 25):
        weeks.append(
            {
                "week": week,
                "theme": f"Youth Theme {week:02d}",
                "cycle": "defensive" if week % 2 else "offensive",
                "teaching_goal": f"Youth goal {week:02d}",
                "coach_notes": f"Youth coach note {week:02d}",
                "sections": [
                    {
                        "name": "Ground Focus",
                        "focus": f"Youth ground focus {week:02d}",
                        "level_1": f"Youth level 1 option {week:02d}",
                        "level_2": f"Youth level 2 option {week:02d}",
                        "coach_notes": f"Youth section note {week:02d}",
                    }
                ],
            }
        )

    weeks[22]["theme"] = "Youth Self-Defense Standing"
    weeks[23]["theme"] = "Youth Self-Defense Ground"
    weeks[22]["sections"][0]["focus"] = "Standing self-defense"
    weeks[23]["sections"][0]["focus"] = "Ground self-defense"
    return weeks


def build_adult_weeks() -> list[dict]:
    weeks = []
    for week in range(1, 25):
        weeks.append(
            {
                "week": week,
                "theme": f"Adult Theme {week:02d}",
                "cycle": "defensive" if week % 2 else "offensive",
                "teaching_goal": f"Adult goal {week:02d}",
                "coach_notes": f"Adult coach note {week:02d}",
                "adult_specific_notes": f"Adult-specific note {week:02d}",
                "sections": [
                    {
                        "name": "Ground Focus",
                        "focus": f"Adult ground focus {week:02d}",
                        "level_1": f"Adult level 1 option {week:02d}",
                        "level_2": f"Adult level 2 option {week:02d}",
                        "coach_notes": f"Adult section note {week:02d}",
                    }
                ],
            }
        )

    weeks[22]["theme"] = "Adult Lower-Body Offense"
    weeks[23]["theme"] = "Adult Lower-Body Defense"
    return weeks


def build_tots_weeks() -> list[dict]:
    cycles = {
        1: "foundation",
        2: "foundation",
        3: "foundation",
        4: "foundation",
        5: "movement",
        6: "movement",
        7: "movement",
        8: "movement",
        9: "partner",
        10: "partner",
        11: "partner",
        12: "review",
    }
    weeks = []
    for week in range(1, 13):
        weeks.append(
            {
                "week": week,
                "cycle": cycles[week],
                "theme": f"Tots Theme {week:02d}",
                "movement_theme": f"Movement theme {week:02d}",
                "game": f"Game {week:02d}",
                "coordination_focus": f"Coordination focus {week:02d}",
                "bjj_exposure": f"BJJ exposure {week:02d}",
                "coach_notes": f"Tots coach note {week:02d}",
            }
        )
    return weeks


def write_theme_map_page(
    repo: Path,
    *,
    relative_path: str,
    page_id: str,
    title: str,
    source_page_id: str,
    weeks: list[dict],
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
{json.dumps({"weeks": weeks}, indent=2)}
```
""",
    )


def seed_repo_with_sources_and_theme_maps(repo: Path) -> None:
    source_dir = repo / "kb" / "sources"
    write_page(
        source_dir / "overview.md",
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
        source_dir / "compendium.md",
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

    write_theme_map_page(
        repo,
        relative_path="kb/curriculum/youth-24-week-theme-map.md",
        page_id="youth-24-week-theme-map",
        title="Youth 24-Week Theme Map",
        source_page_id="source-overview",
        weeks=build_youth_weeks(),
    )
    write_theme_map_page(
        repo,
        relative_path="kb/curriculum/adult-24-week-theme-map.md",
        page_id="adult-24-week-theme-map",
        title="Adult 24-Week Theme Map",
        source_page_id="source-overview",
        weeks=build_adult_weeks(),
    )
    write_theme_map_page(
        repo,
        relative_path="kb/curriculum/tots-12-week-theme-map.md",
        page_id="tots-12-week-theme-map",
        title="Tots 12-Week Theme Map",
        source_page_id="source-compendium",
        weeks=build_tots_weeks(),
    )


def seed_repo_reports(repo: Path) -> None:
    write_page(repo / "generated" / "reports" / "gap-report.md", "# Gap Report\n")
    write_page(repo / "generated" / "reports" / "conflict-report.md", "# Conflict Report\n")
    write_page(repo / "generated" / "reports" / "improvement-report.md", "# Improvement Report\n")


def write_job_file(repo: Path, job_name: str, *, instructions: list[str] | None = None, qa: list[str] | None = None) -> None:
    instruction_lines = "\n".join(f"- {item}" for item in (instructions or [])) or "No additional instructions."
    qa_lines = "\n".join(f"- {item}" for item in (qa or [])) or "No additional Q&A."
    write_page(
        repo / "jobs" / job_name / "job.md",
        f"""---
id: {job_name}
title: "Test Job {job_name}"
generation_targets:
  - curriculum
status: active
transient: false
---
# Test Job

## Purpose

Generate curriculum outputs for testing.

## Instructions

{instruction_lines}

## Q&A

{qa_lines}

## Notes

No extra notes.
""",
    )


def test_generate_curriculum_outputs_creates_expected_program_directories_and_week_files(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(repo, "weekly-curriculum")

    subprocess.run([sys.executable, str(GENERATE_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

    output_root = repo / "generated" / "weekly-curriculum"
    assert (output_root / "curriculum" / "youth" / "week-01-curriculum.md").exists()
    assert (output_root / "curriculum" / "youth" / "week-24-fully-scripted-session.md").exists()
    assert (output_root / "curriculum" / "adult" / "week-24-curriculum.md").exists()
    assert (output_root / "curriculum" / "adult" / "week-24-fully-scripted-session.md").exists()
    assert (output_root / "curriculum" / "tots" / "week-12-curriculum.md").exists()
    assert (output_root / "curriculum" / "tots" / "week-12-coach-guide.md").exists()
    assert (output_root / "curriculum" / "tots-syllabus.md").exists()
    assert (output_root / "curriculum" / "youth-syllabus.md").exists()
    assert (output_root / "curriculum" / "adult-syllabus.md").exists()
    assert (output_root / "reports" / "gap-report.md").exists()
    assert (output_root / "reports" / "conflict-report.md").exists()
    assert (output_root / "reports" / "improvement-report.md").exists()
    assert (output_root / "new-facts" / "index.md").exists()
    assert not (repo / "generated" / "curriculum").exists()

    assert len(list((output_root / "curriculum" / "youth").glob("*.md"))) == 96
    assert len(list((output_root / "curriculum" / "adult").glob("*.md"))) == 96
    assert len(list((output_root / "curriculum" / "tots").glob("*.md"))) == 48


def test_generate_curriculum_outputs_include_level_sections_and_program_specific_notes(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(repo, "weekly-curriculum")

    subprocess.run([sys.executable, str(GENERATE_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

    output_root = repo / "generated" / "weekly-curriculum" / "curriculum"
    youth_text = (output_root / "youth" / "week-01-curriculum.md").read_text(encoding="utf-8")
    adult_text = (output_root / "adult" / "week-01-curriculum.md").read_text(encoding="utf-8")
    adult_lower_body_text = (
        output_root / "adult" / "week-24-curriculum.md"
    ).read_text(encoding="utf-8")
    tots_text = (output_root / "tots" / "week-01-curriculum.md").read_text(encoding="utf-8")
    youth_syllabus_text = (output_root / "youth-syllabus.md").read_text(encoding="utf-8")

    assert "- Week: 01" in youth_text
    assert "- Cycle: defensive" in youth_text
    assert "- Theme: Youth Theme 01" in youth_text
    assert "## Level 1" in youth_text
    assert "## Level 2" in youth_text
    assert "## Adult-Specific Notes" in adult_text
    assert "Adult Lower-Body Defense" in adult_lower_body_text
    assert "- Cycle: foundation" in tots_text
    assert "- Movement Theme: Movement theme 01" in tots_text
    assert "## Movement Theme" in tots_text
    assert "## Game" in tots_text
    assert "| Week | Cycle | Theme | Description | Main Goal |" in youth_syllabus_text
    assert "| 01 | defensive | Youth Theme 01 | Youth ground focus 01 | Youth goal 01 |" in youth_syllabus_text


def test_generate_curriculum_outputs_do_not_modify_kb_and_emit_empty_new_facts_when_no_human_deltas(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(repo, "weekly-curriculum")

    kb_hash_before = hash_tree(repo / "kb")

    subprocess.run([sys.executable, str(GENERATE_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

    kb_hash_after = hash_tree(repo / "kb")
    new_facts_dir = repo / "generated" / "weekly-curriculum" / "new-facts"
    index_text = (new_facts_dir / "index.md").read_text(encoding="utf-8")

    assert kb_hash_after == kb_hash_before
    assert list(new_facts_dir.glob("fact-*.md")) == []
    assert "No candidate new facts were found in this job." in index_text


def test_generate_curriculum_outputs_emit_candidate_new_fact_files_for_non_redundant_human_deltas(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(
        repo,
        "weekly-curriculum",
        qa=["Add a coaches-only review checkpoint after week 12."],
    )

    subprocess.run([sys.executable, str(GENERATE_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

    new_facts_dir = repo / "generated" / "weekly-curriculum" / "new-facts"
    fact_paths = sorted(new_facts_dir.glob("fact-*.md"))
    index_text = (new_facts_dir / "index.md").read_text(encoding="utf-8")
    fact_text = fact_paths[0].read_text(encoding="utf-8")

    assert len(fact_paths) == 1
    assert "Add a coaches-only review checkpoint after week 12." in fact_text
    assert "Suggested Raw Filename:" in fact_text
    assert "Suggested KB Target Area:" in fact_text
    assert "Why It Appears New" in fact_text
    assert fact_paths[0].name in index_text


def test_generate_curriculum_outputs_reject_reserved_job_names(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(repo, "reports")

    result = subprocess.run(
        [sys.executable, str(GENERATE_SCRIPT), str(repo), "--job-name", "reports"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "reserved generated path" in result.stderr


def test_generate_curriculum_outputs_rerun_replaces_job_workspace_contents(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(
        repo,
        "weekly-curriculum",
        qa=["Add a coaches-only review checkpoint after week 12."],
    )

    subprocess.run([sys.executable, str(GENERATE_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)
    new_facts_dir = repo / "generated" / "weekly-curriculum" / "new-facts"
    assert len(list(new_facts_dir.glob("fact-*.md"))) == 1

    write_job_file(repo, "weekly-curriculum")
    subprocess.run([sys.executable, str(GENERATE_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

    assert list(new_facts_dir.glob("fact-*.md")) == []
    assert "No candidate new facts were found in this job." in (new_facts_dir / "index.md").read_text(encoding="utf-8")
