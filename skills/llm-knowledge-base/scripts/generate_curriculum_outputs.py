from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import ensure_dir, parse_frontmatter, write_text


PROGRAM_CONFIG = {
    "youth": {
        "page_path": "kb/curriculum/youth-24-week-theme-map.md",
        "class_length": "60 minutes",
        "program_title": "Youth",
    },
    "adult": {
        "page_path": "kb/curriculum/adult-24-week-theme-map.md",
        "class_length": "60 minutes",
        "program_title": "Adult",
    },
    "tots": {
        "page_path": "kb/curriculum/tots-12-week-theme-map.md",
        "class_length": "30 minutes",
        "program_title": "Tots",
    },
}

OUTPUT_TYPES = (
    "curriculum",
    "quick-outline",
    "coach-guide",
    "fully-scripted-session",
)


def prose(text: str) -> str:
    return text.rstrip().rstrip(".")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unspecified"


def build_output_filename(week: dict, output_type: str) -> str:
    week_number = int(week["week"])
    cycle = slugify(str(week.get("cycle", "unspecified")))
    theme_slug = slugify(str(week.get("theme", "unspecified")))
    file_type = {
        "curriculum": "curriculum",
        "quick-outline": "quick-outline",
        "coach-guide": "coach-guide",
        "fully-scripted-session": "scripted-session",
    }[output_type]
    return f"week-{week_number:02d}_[{cycle}]_[{theme_slug}]_[{file_type}].md"


def extract_json_block(body: str) -> dict:
    start = body.find("```json")
    if start == -1:
        raise ValueError("missing ```json block in curriculum page body")
    start += len("```json")
    end = body.find("```", start)
    if end == -1:
        raise ValueError("unterminated ```json block in curriculum page body")
    payload = body[start:end].strip()
    return json.loads(payload)


def load_program_data(repo_root: Path, program: str) -> tuple[dict, list[dict]]:
    config = PROGRAM_CONFIG[program]
    page_path = repo_root / config["page_path"]
    metadata, body = parse_frontmatter(page_path.read_text(encoding="utf-8"))
    payload = extract_json_block(body)
    weeks = payload.get("weeks")
    if not isinstance(weeks, list):
        raise ValueError(f"weeks payload must be a list in {page_path}")
    return metadata, weeks


def render_youth_or_adult_curriculum(program: str, metadata: dict, week: dict) -> str:
    program_title = PROGRAM_CONFIG[program]["program_title"]
    lines = [
        f"# {program_title} Week {week['week']:02d} Curriculum",
        "",
        "## Snapshot",
        f"- Theme: {week['theme']}",
        f"- Cycle: {week.get('cycle', 'unspecified')}",
        f"- Teaching Goal: {week.get('teaching_goal', 'Not specified')}",
        f"- Class Length: {PROGRAM_CONFIG[program]['class_length']}",
        f"- Source Basis: {', '.join(metadata.get('source_refs', [])) or 'Not specified'}",
        "",
        "## Coach Notes",
        week.get("coach_notes", "No coach notes provided."),
    ]
    if program == "adult":
        lines.extend(
            [
                "",
                "## Adult-Specific Notes",
                week.get("adult_specific_notes", "Use the youth framework and add adult-specific context where needed."),
            ]
        )

    for section in week.get("sections", []):
        lines.extend(
            [
                "",
                f"## {section['name']}",
                f"- Focus: {section.get('focus', 'Not specified')}",
                f"- Coach Notes: {section.get('coach_notes', week.get('coach_notes', 'Not specified'))}",
                "",
                "## Level 1",
                f"- {section.get('level_1', 'Not specified')}",
                "",
                "## Level 2",
                f"- {section.get('level_2', 'Not specified')}",
            ]
        )

    return "\n".join(lines) + "\n"


def render_tots_curriculum(metadata: dict, week: dict) -> str:
    lines = [
        f"# Tots Week {week['week']:02d} Curriculum",
        "",
        "## Snapshot",
        f"- Theme: {week['theme']}",
        f"- Class Length: {PROGRAM_CONFIG['tots']['class_length']}",
        f"- Source Basis: {', '.join(metadata.get('source_refs', [])) or 'Not specified'}",
        "",
        "## Movement Theme",
        week.get("movement_theme", "Not specified"),
        "",
        "## Game",
        week.get("game", "Not specified"),
        "",
        "## Coordination Focus",
        week.get("coordination_focus", "Not specified"),
        "",
        "## Intro Grappling Exposure",
        week.get("bjj_exposure", "Not specified"),
        "",
        "## Coach Notes",
        week.get("coach_notes", "No coach notes provided."),
    ]
    return "\n".join(lines) + "\n"


def render_curriculum(program: str, metadata: dict, week: dict) -> str:
    if program == "tots":
        return render_tots_curriculum(metadata, week)
    return render_youth_or_adult_curriculum(program, metadata, week)


def render_quick_outline(program: str, week: dict) -> str:
    lines = [
        f"# {PROGRAM_CONFIG[program]['program_title']} Week {week['week']:02d} Quick Outline",
        "",
        f"- Theme: {week['theme']}",
    ]
    if program == "tots":
        lines.extend(
            [
                f"- Movement Theme: {week.get('movement_theme', 'Not specified')}",
                f"- Game: {week.get('game', 'Not specified')}",
                f"- Coordination Focus: {week.get('coordination_focus', 'Not specified')}",
                f"- BJJ Exposure: {week.get('bjj_exposure', 'Not specified')}",
            ]
        )
    else:
        lines.extend(
            [
                f"- Cycle: {week.get('cycle', 'unspecified')}",
                f"- Teaching Goal: {week.get('teaching_goal', 'Not specified')}",
            ]
        )
        for section in week.get("sections", []):
            lines.append(f"- {section['name']}: {section.get('focus', 'Not specified')}")
    return "\n".join(lines) + "\n"


def render_coach_guide(program: str, week: dict) -> str:
    lines = [
        f"# {PROGRAM_CONFIG[program]['program_title']} Week {week['week']:02d} Coach Guide",
        "",
        "## Weekly Intent",
        week.get("teaching_goal", week.get("theme", "Not specified")),
        "",
        "## Coaching Emphasis",
        week.get("coach_notes", "No coach notes provided."),
        "",
        "## Safety Notes",
    ]
    if program == "tots":
        lines.append("Keep rounds short, maintain high engagement, and prioritize movement quality over technical volume.")
        lines.extend(
            [
                "",
                "## Scaling Options",
                "- Reduce complexity by shrinking the movement chain.",
                "- Increase challenge by adding reaction and direction changes.",
            ]
        )
    else:
        lines.append("Match resistance to student readiness, reinforce tapping and partner care, and scale pace before complexity.")
        lines.extend(
            [
                "",
                "## Scaling Options",
                "- Level 1 should focus on core mechanics and one clean finish or escape path.",
                "- Level 2 should add chain options, timing, or more live reactions without changing the theme.",
            ]
        )
        if program == "adult":
            lines.extend(
                [
                    "",
                    "## Adult-Specific Notes",
                    week.get("adult_specific_notes", "Use the youth framework and add adult-specific context where needed."),
                ]
            )
    return "\n".join(lines) + "\n"


def render_fully_scripted_session(program: str, week: dict) -> str:
    title = PROGRAM_CONFIG[program]["program_title"]
    lines = [
        f"# {title} Week {week['week']:02d} Fully Scripted Session",
        "",
        "## Opening Script",
        f"Introduce the theme: {prose(week['theme'])}. Tell the class the goal is {prose(week.get('teaching_goal', week['theme']))}.",
        "",
        "## Warm-Up Block",
    ]
    if program == "tots":
        lines.extend(
            [
                f"Run a movement-focused warm-up around {week.get('movement_theme', 'the theme')} and keep the pace playful.",
                "",
                "## Main Activity Block",
                f"Play {week.get('game', 'the game')} and use short resets to reinforce {week.get('coordination_focus', 'coordination')}.",
                "",
                "## Intro Grappling Block",
                f"Expose the students to {week.get('bjj_exposure', 'the intro grappling skill')} with simple cues and lots of praise.",
            ]
        )
    else:
        lines.append("Use a brief, topic-aware warm-up and set the expectation that the class will build one connected theme.")
        for section in week.get("sections", []):
            lines.extend(
                [
                    "",
                    f"## {section['name']} Script",
                    f"Show the core idea first: {prose(section.get('focus', 'Not specified'))}.",
                    f"Teach Level 1 as the base pattern: {prose(section.get('level_1', 'Not specified'))}.",
                    f"Layer Level 2 only after the room is stable: {prose(section.get('level_2', 'Not specified'))}.",
                    f"Repeat the coach emphasis: {prose(section.get('coach_notes', week.get('coach_notes', 'Not specified')))}.",
                ]
            )
        if program == "adult":
            lines.extend(
                [
                    "",
                    "## Adult-Specific Notes",
                    week.get("adult_specific_notes", "Use the youth framework and add adult-specific context where needed."),
                ]
            )

    lines.extend(
        [
            "",
            "## Closing Script",
            "Recap the main idea, reinforce the best example from the room, and set the expectation for live application.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_output(program: str, output_type: str, metadata: dict, week: dict) -> str:
    if output_type == "curriculum":
        return render_curriculum(program, metadata, week)
    if output_type == "quick-outline":
        return render_quick_outline(program, week)
    if output_type == "coach-guide":
        return render_coach_guide(program, week)
    if output_type == "fully-scripted-session":
        return render_fully_scripted_session(program, week)
    raise ValueError(f"unknown output type: {output_type}")


def generate_outputs(repo_root: Path) -> None:
    for program in PROGRAM_CONFIG:
        metadata, weeks = load_program_data(repo_root, program)
        output_dir = ensure_dir(repo_root / "generated" / "curriculum" / program)
        for path in output_dir.glob("*.md"):
            path.unlink()
        for week in weeks:
            for output_type in OUTPUT_TYPES:
                filename = build_output_filename(week, output_type)
                content = render_output(program, output_type, metadata, week)
                write_text(output_dir / filename, content, overwrite=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate weekly curriculum markdown outputs from KB theme maps.")
    parser.add_argument("repo_root", help="Path to the repo root.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    generate_outputs(repo_root)


if __name__ == "__main__":
    main()
