import json
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

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


def write_fully_scripted_example(repo: Path, job_name: str) -> None:
    write_page(
        repo / "jobs" / job_name / "examples" / "fully-scripted-session" / "week-01-offensive-cycle.md",
        """---
notes:
  - Keep the overall fully scripted session scaffold intact.
  - Use this example to shape the Primary Focus section into a structured lesson block.
  - Favor compact coach-facing bullet points.
  - Bold important or large distinct parts of the lesson.
  - Add tips or cues if it's available from the knowledge base.
  - Add options for constraints-led approach (CLA) or live situational training if there are good options available for that section.
lesson_label: Teaching Flow
coaching_label: Coach Cue
level_1_label: Base Layer
level_2_label: Advanced Layer
outcome_label: Win Condition
cla_label: Positional Rounds
---
## Week 1 (Offensive Cycle)
- Theme: Double Leg to Side Control to Americana
- Teaching Goal: Build a connected offensive sequence from takedown entry to stable top control and a clean Americana finish.
- Class Length: 60 minutes

## Opening Script
Introduce the theme: Double Leg to Side Control to Americana. Tell the class the goal is to build one connected offensive sequence from the feet to a stable finish on the ground.

## Warm-Up Options
- **Movement Based**:
  - Duck walks
- **Drill Based**:
  - Double leg pickups

## Lesson: Double leg - Side control - Americana
- **Takedown**
  - Coaching tip: "Level change first, then penetration step/duck walk"
  - Level 1: Double leg (low amplitude/high amplitude)
  - Level 2: Double leg (chain attack)
  - Outcome: Clean top -> side control
- **Ground: Side Control (Top)**
  - **Secure: Crossface + underhook**
  - **Level 2: Transition between various side control pins**
  - **Submission: Americana**
- **CLA/Situational Rolling Options**:
  - Start with crossface + underhook, roll until escape or americana or kimura grip no submission.
""",
    )


def write_job_file(
    repo: Path,
    job_name: str,
    *,
    instructions: list[str] | None = None,
    qa: list[str] | None = None,
    include_examples: bool = False,
) -> None:
    instruction_lines = "\n".join(f"- {item}" for item in (instructions or [])) or "No additional instructions."
    qa_lines = "\n".join(f"- {item}" for item in (qa or [])) or "No additional Q&A."
    examples_block = ""
    if include_examples:
        examples_block = f"""  examples:
    fully-scripted-session:
      - jobs/{job_name}/examples/fully-scripted-session/week-01-offensive-cycle.md
"""
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
{examples_block}options:
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
    if include_examples:
        write_fully_scripted_example(repo, job_name)


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


def test_generate_curriculum_outputs_render_structured_primary_focus_in_fully_scripted_sessions(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(repo, "weekly-curriculum")

    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

    youth_fully_scripted = (
        repo / "generated" / "weekly-curriculum" / "curriculum" / "youth" / "week-01-fully-scripted-session.md"
    ).read_text(encoding="utf-8")
    adult_fully_scripted = (
        repo / "generated" / "weekly-curriculum" / "curriculum" / "adult" / "week-01-fully-scripted-session.md"
    ).read_text(encoding="utf-8")

    assert "## Ground Focus Script" in youth_fully_scripted
    assert "### Week 1 (DEFENSIVE CYCLE)" in youth_fully_scripted
    assert "#### FLOW: Youth ground focus 01" in youth_fully_scripted
    assert '- **Ground Focus**' in youth_fully_scripted
    assert '- Coaching tip: "Youth section note 01"' in youth_fully_scripted
    assert "- L1: Youth level 1 option 01" in youth_fully_scripted
    assert "- L2: Youth level 2 option 01" in youth_fully_scripted
    assert "- Outcome: Youth goal 01" in youth_fully_scripted
    assert "## Adult-Specific Notes" in adult_fully_scripted


def test_generate_curriculum_outputs_use_fully_scripted_example_style_when_configured(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)
    write_job_file(repo, "weekly-curriculum", include_examples=True)

    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

    adult_fully_scripted = (
        repo / "generated" / "weekly-curriculum" / "curriculum" / "adult" / "week-01-fully-scripted-session.md"
    ).read_text(encoding="utf-8")

    assert "## Ground Focus Script" in adult_fully_scripted
    assert "### Teaching Flow: Adult ground focus 01" in adult_fully_scripted
    assert "- **Ground Focus**" in adult_fully_scripted
    assert '- Coach Cue: "Adult section note 01"' in adult_fully_scripted
    assert "- Base Layer: Adult level 1 option 01" in adult_fully_scripted
    assert "- Advanced Layer: Adult level 2 option 01" in adult_fully_scripted
    assert "- Win Condition: Adult goal 01" in adult_fully_scripted
    assert "### Week 1 (DEFENSIVE CYCLE)" not in adult_fully_scripted


def test_generate_curriculum_outputs_split_takedown_and_ground_blocks_when_kb_supports_it(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)

    adult_weeks = build_adult_weeks()
    adult_weeks[0] = {
        "week": 1,
        "theme": "Double Leg And Body-Lock Entries To Passing Finish",
        "cycle": "offensive",
        "teaching_goal": "Connect wrestling-style entries to immediate top control and passing follow-through.",
        "coach_notes": "The takedown and the pass must feel like one connected idea.",
        "adult_specific_notes": "Use wall or boundary awareness if the room layout allows, while keeping the main sequence mat-centered.",
        "sections": [
            {
                "name": "Primary Focus",
                "focus": "Double leg or body-lock entry leading to stable top position and first pass.",
                "level_1": "Finish the takedown and stabilize in half guard top or headquarters.",
                "level_2": "Continue directly into a knee-cut or pressure pass before the guard resets.",
                "coach_notes": "The shoulders should stay over the hips through the finish.",
            }
        ],
    }
    write_theme_map_page(
        repo,
        relative_path="kb/curriculum/adult-24-week-theme-map.md",
        page_id="adult-24-week-theme-map",
        title="Adult 24-Week Theme Map",
        source_page_id="source-overview",
        weeks=adult_weeks,
    )
    write_job_file(repo, "weekly-curriculum", include_examples=True)

    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

    adult_fully_scripted = (
        repo / "generated" / "weekly-curriculum" / "curriculum" / "adult" / "week-01-fully-scripted-session.md"
    ).read_text(encoding="utf-8")

    assert "### Teaching Flow: Double leg or body-lock entry leading to stable top position and first pass" in adult_fully_scripted
    assert "- **Takedown**" in adult_fully_scripted
    assert "- Base Layer: Finish the takedown and stabilize in half guard top or headquarters" in adult_fully_scripted
    assert "- Win Condition: Connect wrestling-style entries to immediate top control and passing follow-through" in adult_fully_scripted
    assert "- **Ground: Passing Finish**" in adult_fully_scripted
    assert "- Advanced Layer: Continue directly into a knee-cut or pressure pass before the guard resets" in adult_fully_scripted


def test_generate_curriculum_outputs_split_ground_and_submission_blocks_when_kb_supports_it(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)
    seed_repo_reports(repo)

    adult_weeks = build_adult_weeks()
    adult_weeks[0] = {
        "week": 1,
        "theme": "Side Control Control To Americana",
        "cycle": "offensive",
        "teaching_goal": "Use top control to build one reliable attack route instead of a loose collection of submissions.",
        "coach_notes": "Position first, pressure second, finish third.",
        "adult_specific_notes": "Adults can explore follow-up transitions when the americana defense is stubborn, but the base attack stays primary.",
        "sections": [
            {
                "name": "Primary Focus",
                "focus": "Side control pressure, far-side isolation, and americana mechanics.",
                "level_1": "Secure side control and finish the americana with clean elbow positioning.",
                "level_2": "Flow from the americana threat into a straight-arm or mount transition when the partner defends.",
                "coach_notes": "Top pressure should make the isolation easier, not compensate for weak grips.",
            }
        ],
    }
    write_theme_map_page(
        repo,
        relative_path="kb/curriculum/adult-24-week-theme-map.md",
        page_id="adult-24-week-theme-map",
        title="Adult 24-Week Theme Map",
        source_page_id="source-overview",
        weeks=adult_weeks,
    )
    write_job_file(repo, "weekly-curriculum", include_examples=True)

    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "weekly-curriculum"], check=True)

    adult_fully_scripted = (
        repo / "generated" / "weekly-curriculum" / "curriculum" / "adult" / "week-01-fully-scripted-session.md"
    ).read_text(encoding="utf-8")

    assert "- **Ground: Side Control (Top)**" in adult_fully_scripted
    assert "- Base Layer: Secure side control and finish the americana with clean elbow positioning" in adult_fully_scripted
    assert "- **Submission: Americana**" in adult_fully_scripted
    assert "- Advanced Layer: Flow from the americana threat into a straight-arm or mount transition when the partner defends" in adult_fully_scripted


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
