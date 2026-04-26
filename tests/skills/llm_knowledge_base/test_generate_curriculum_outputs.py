import json
import subprocess
import sys
from pathlib import Path

INIT_SCRIPT = Path("skills/llm-knowledge-base/scripts/init_repo.py").resolve()
GENERATE_SCRIPT = Path("skills/llm-knowledge-base/scripts/generate_curriculum_outputs.py").resolve()


def write_page(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
    weeks = []
    for week in range(1, 13):
        weeks.append(
            {
                "week": week,
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


def test_generate_curriculum_outputs_creates_expected_program_directories_and_week_files(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)

    subprocess.run([sys.executable, str(GENERATE_SCRIPT), str(repo)], check=True)

    assert (repo / "generated" / "curriculum" / "youth" / "week-01-curriculum.md").exists()
    assert (repo / "generated" / "curriculum" / "youth" / "week-24-fully-scripted-session.md").exists()
    assert (repo / "generated" / "curriculum" / "adult" / "week-24-curriculum.md").exists()
    assert (repo / "generated" / "curriculum" / "adult" / "week-24-fully-scripted-session.md").exists()
    assert (repo / "generated" / "curriculum" / "tots" / "week-12-curriculum.md").exists()
    assert (repo / "generated" / "curriculum" / "tots" / "week-12-coach-guide.md").exists()

    assert len(list((repo / "generated" / "curriculum" / "youth").glob("*.md"))) == 96
    assert len(list((repo / "generated" / "curriculum" / "adult").glob("*.md"))) == 96
    assert len(list((repo / "generated" / "curriculum" / "tots").glob("*.md"))) == 48


def test_generate_curriculum_outputs_include_level_sections_and_program_specific_notes(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_repo_with_sources_and_theme_maps(repo)

    subprocess.run([sys.executable, str(GENERATE_SCRIPT), str(repo)], check=True)

    youth_text = (repo / "generated" / "curriculum" / "youth" / "week-01-curriculum.md").read_text(encoding="utf-8")
    adult_text = (repo / "generated" / "curriculum" / "adult" / "week-01-curriculum.md").read_text(encoding="utf-8")
    adult_lower_body_text = (
        repo / "generated" / "curriculum" / "adult" / "week-24-curriculum.md"
    ).read_text(encoding="utf-8")
    tots_text = (repo / "generated" / "curriculum" / "tots" / "week-01-curriculum.md").read_text(encoding="utf-8")

    assert "## Level 1" in youth_text
    assert "## Level 2" in youth_text
    assert "## Adult-Specific Notes" in adult_text
    assert "Adult Lower-Body Defense" in adult_lower_body_text
    assert "## Movement Theme" in tots_text
    assert "## Game" in tots_text
