import json
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

import pytest

REPO_ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[3]
if str(REPO_ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT_FOR_IMPORTS))
SKILL_SCRIPTS_FOR_IMPORTS = REPO_ROOT_FOR_IMPORTS / "skills" / "llm-knowledge-base" / "scripts"
if str(SKILL_SCRIPTS_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(SKILL_SCRIPTS_FOR_IMPORTS))

from repo_generators import curriculum
from run_generation import load_job_spec

INIT_SCRIPT = Path("skills/llm-knowledge-base/scripts/init_repo.py").resolve()
RUN_SCRIPT = Path("skills/llm-knowledge-base/scripts/run_generation.py").resolve()


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


def write_poisoned_kb_week_maps(repo: Path) -> None:
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
        weeks=[
            {
                "week": 1,
                "theme": "KB Youth Poison Theme",
                "cycle": "defensive",
                "teaching_goal": "KB youth poison goal",
                "coach_notes": "KB youth poison coach notes",
                "sections": [
                    {
                        "name": "Ground Focus",
                        "focus": "KB youth poison focus",
                        "level_1": "KB youth poison level 1",
                        "level_2": "KB youth poison level 2",
                        "coach_notes": "KB youth poison section note",
                    }
                ],
            }
        ],
    )
    write_theme_map_page(
        repo,
        relative_path="kb/curriculum/adult-24-week-theme-map.md",
        page_id="adult-24-week-theme-map",
        title="Adult 24-Week Theme Map",
        source_page_id="source-overview",
        weeks=[
            {
                "week": 1,
                "theme": "KB Adult Poison Theme",
                "cycle": "defensive",
                "teaching_goal": "KB adult poison goal",
                "coach_notes": "KB adult poison coach notes",
                "adult_specific_notes": "KB adult poison specific notes",
                "sections": [
                    {
                        "name": "Ground Focus",
                        "focus": "KB adult poison focus",
                        "level_1": "KB adult poison level 1",
                        "level_2": "KB adult poison level 2",
                        "coach_notes": "KB adult poison section note",
                    }
                ],
            }
        ],
    )
    write_theme_map_page(
        repo,
        relative_path="kb/curriculum/tots-12-week-theme-map.md",
        page_id="tots-12-week-theme-map",
        title="Tots 12-Week Theme Map",
        source_page_id="source-compendium",
        weeks=[
            {
                "week": 1,
                "cycle": "foundation",
                "theme": "KB Tots Poison Theme",
                "movement_theme": "KB tots poison movement",
                "game": "KB tots poison game",
                "coordination_focus": "KB tots poison focus",
                "bjj_exposure": "KB tots poison exposure",
                "coach_notes": "KB tots poison coach notes",
            }
        ],
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
        repo / "jobs" / job_name / "job.yaml",
        f"""id: {job_name}
title: Test Job {job_name}
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
""",
    )
    write_page(
        repo / "jobs" / job_name / "notes.md",
        f"""# Test Job

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


def remove_kb_week_maps(repo: Path) -> None:
    for relative_path in (
        "kb/curriculum/youth-24-week-theme-map.md",
        "kb/curriculum/adult-24-week-theme-map.md",
        "kb/curriculum/tots-12-week-theme-map.md",
    ):
        path = repo / relative_path
        if path.exists():
            path.unlink()


def write_generated_week_map_page(
    repo: Path,
    *,
    program: str,
    page_id: str,
    title: str,
    source_kb_pages: list[str],
    weeks: list[dict],
) -> None:
    filename_by_program = {
        "adult": "adult-24-week-theme-map.md",
        "youth": "youth-24-week-theme-map.md",
        "tots": "tots-12-week-theme-map.md",
    }
    source_kb_pages_text = "".join(f"  - {source_page}\n" for source_page in source_kb_pages)
    write_page(
        repo / "generated" / "weekly-curriculum" / "week-maps" / filename_by_program[program],
        f"""---
id: {page_id}
type: generated-curriculum-candidate
title: "{title}"
status: active
source_kb_pages:
{source_kb_pages_text}generation_notes:
  - synthesized for boundary testing
warnings:
  - none
confidence: 0.95
---
# {title}

Candidate week map for {program}.

```json
{json.dumps({"weeks": weeks}, indent=2)}
```
""",
    )


def write_curriculum_framework_page(repo: Path, page_id: str, title: str, body: str) -> None:
    write_page(
        repo / "kb" / "curriculum" / f"{page_id}.md",
        f"""---
id: {page_id}
type: curriculum-unit
title: "{title}"
status: active
confidence: 0.8
claim_label: fact
source_refs:
  - source-overview#chunk-001
related_pages: []
---
# {title}

{body}
""",
    )


def seed_minimal_framework_repo(repo: Path) -> None:
    write_page(
        repo / "kb" / "sources" / "overview.md",
        """---
id: source-overview
type: source
title: Overview
status: active
confidence: 1.0
source_refs: []
related_pages: []
---
# Overview
""",
    )
    write_curriculum_framework_page(
        repo,
        "curriculum-week-design-rules",
        "Curriculum Week Design Rules",
        "Weekly curriculum design follows a fixed set of rules intended to keep theme, progression, and coach usability aligned.",
    )
    write_curriculum_framework_page(
        repo,
        "youth-24-week-curriculum-framework",
        "Youth 24-Week Curriculum Framework",
        "The youth framework defines the sequencing constraints for the 24-week calendar.",
    )
    write_curriculum_framework_page(
        repo,
        "adult-24-week-curriculum-framework",
        "Adult 24-Week Curriculum Framework",
        "The adult framework defines the sequencing constraints for the 24-week calendar.",
    )
    write_curriculum_framework_page(
        repo,
        "tots-12-week-curriculum-framework",
        "Tots 12-Week Curriculum Framework",
        "The tots framework defines the sequencing constraints for the 12-week calendar.",
    )


def write_stage2_job_file(repo: Path, job_name: str) -> None:
    write_page(
        repo / "jobs" / job_name / "job.yaml",
        f"""id: {job_name}
title: Test Job {job_name}
generator: curriculum
generation_targets:
  - curriculum
status: active
transient: false
inputs:
  kb_pages:
    - kb/curriculum/curriculum-week-design-rules.md
    - kb/curriculum/youth-24-week-curriculum-framework.md
    - kb/curriculum/adult-24-week-curriculum-framework.md
    - kb/curriculum/tots-12-week-curriculum-framework.md
options:
  include_reports: true
  emit_new_facts: true
""",
    )
    write_page(
        repo / "jobs" / job_name / "notes.md",
        """# Test Job

## Purpose

Generate curriculum outputs for testing.

## Instructions

- Use generated week maps only.

## Q&A

- No additional Q&A.

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

    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

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


def test_generate_curriculum_outputs_writes_generated_week_maps_and_uses_them(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_minimal_framework_repo(repo)
    write_poisoned_kb_week_maps(repo)
    write_generated_week_map_page(
        repo,
        program="youth",
        page_id="generated-youth-week-map",
        title="Youth Generated Week Map",
        source_kb_pages=["kb/curriculum/youth-24-week-curriculum-framework.md"],
        weeks=[
            {
                "week": 1,
                "theme": "Generated Youth Sentinel Theme",
                "cycle": "defensive",
                "teaching_goal": "Generated youth sentinel goal",
                "coach_notes": "Generated youth sentinel coach notes",
                "sections": [
                    {
                        "name": "Ground Focus",
                        "focus": "Generated youth sentinel focus",
                        "level_1": "Generated youth sentinel level 1",
                        "level_2": "Generated youth sentinel level 2",
                        "coach_notes": "Generated youth sentinel section note",
                    }
                ],
            }
        ],
    )
    write_generated_week_map_page(
        repo,
        program="adult",
        page_id="generated-adult-week-map",
        title="Adult Generated Week Map",
        source_kb_pages=["kb/curriculum/adult-24-week-curriculum-framework.md"],
        weeks=[
            {
                "week": 1,
                "theme": "Generated Adult Sentinel Theme",
                "cycle": "defensive",
                "teaching_goal": "Generated adult sentinel goal",
                "coach_notes": "Generated adult sentinel coach notes",
                "adult_specific_notes": "Generated adult sentinel specific notes",
                "sections": [
                    {
                        "name": "Ground Focus",
                        "focus": "Generated adult sentinel focus",
                        "level_1": "Generated adult sentinel level 1",
                        "level_2": "Generated adult sentinel level 2",
                        "coach_notes": "Generated adult sentinel section note",
                    }
                ],
            }
        ],
    )
    write_generated_week_map_page(
        repo,
        program="tots",
        page_id="generated-tots-week-map",
        title="Tots Generated Week Map",
        source_kb_pages=["kb/curriculum/tots-12-week-curriculum-framework.md"],
        weeks=[
            {
                "week": 1,
                "cycle": "foundation",
                "theme": "Generated Tots Sentinel Theme",
                "movement_theme": "Generated tots sentinel movement",
                "game": "Generated tots sentinel game",
                "coordination_focus": "Generated tots sentinel focus",
                "bjj_exposure": "Generated tots sentinel exposure",
                "coach_notes": "Generated tots sentinel coach notes",
            }
        ],
    )
    seed_repo_reports(repo)
    write_stage2_job_file(repo, "weekly-curriculum")

    result = subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    generated_week_map = repo / "generated" / "weekly-curriculum" / "week-maps" / "adult-24-week-theme-map.md"
    generated_week_map_text = generated_week_map.read_text(encoding="utf-8")
    adult_curriculum_text = (
        repo / "generated" / "weekly-curriculum" / "curriculum" / "adult" / "week-01-curriculum.md"
    ).read_text(encoding="utf-8")

    assert generated_week_map.exists()
    assert "type: generated-curriculum-candidate" in generated_week_map_text
    assert "```json" in generated_week_map_text
    assert (repo / "generated" / "weekly-curriculum" / "curriculum" / "adult" / "week-01-curriculum.md").exists()
    assert "Generated Adult Sentinel Theme" in adult_curriculum_text
    assert "Generated adult sentinel focus" in adult_curriculum_text
    assert "Generated adult sentinel goal" in adult_curriculum_text
    assert "KB adult poison focus" not in adult_curriculum_text


def test_generate_curriculum_outputs_fail_when_generated_week_maps_are_missing(tmp_path, monkeypatch):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_minimal_framework_repo(repo)
    write_poisoned_kb_week_maps(repo)
    seed_repo_reports(repo)
    write_stage2_job_file(repo, "weekly-curriculum")
    job_spec, job_context = load_job_spec(repo, "weekly-curriculum")

    generated_week_map_root = repo / "generated" / "weekly-curriculum" / "week-maps"
    original_write_text = curriculum.write_text

    def guarded_write_text(path: Path, content: str, overwrite: bool = False) -> None:
        if path.is_relative_to(generated_week_map_root):
            return
        original_write_text(path, content, overwrite=overwrite)

    monkeypatch.setattr(curriculum, "write_text", guarded_write_text)

    with pytest.raises(FileNotFoundError, match="generated week map"):
        curriculum.generate(repo, job_spec, job_context)


def test_generate_curriculum_outputs_include_level_sections_and_program_specific_notes(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(repo, "weekly-curriculum")

    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

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


def test_generate_curriculum_outputs_quick_outline_does_not_repeat_metadata_fields(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(repo, "weekly-curriculum")

    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

    adult_quick_outline = (
        repo / "generated" / "weekly-curriculum" / "curriculum" / "adult" / "week-03-quick-outline.md"
    ).read_text(encoding="utf-8")

    assert adult_quick_outline.count("- Theme: Adult Theme 03") == 1
    assert adult_quick_outline.count("- Cycle: defensive") == 1
    assert adult_quick_outline.count("- Teaching Goal: Adult goal 03") == 1
    assert "- Ground Focus: Adult ground focus 03" in adult_quick_outline


def test_generate_curriculum_outputs_do_not_modify_kb_and_emit_empty_new_facts_when_no_human_deltas(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(repo, "weekly-curriculum")

    kb_hash_before = hash_tree(repo / "kb")

    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

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

    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

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
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "reports"],
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

    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)
    new_facts_dir = repo / "generated" / "weekly-curriculum" / "new-facts"
    assert len(list(new_facts_dir.glob("fact-*.md"))) == 1

    write_job_file(repo, "weekly-curriculum")
    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

    assert list(new_facts_dir.glob("fact-*.md")) == []
    assert "No candidate new facts were found in this job." in (new_facts_dir / "index.md").read_text(encoding="utf-8")
