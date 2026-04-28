from __future__ import annotations

import json
import re
import shutil
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

OUTPUT_TYPES = ("curriculum", "quick-outline", "coach-guide", "fully-scripted-session")
RESERVED_GENERATED_NAMES = {"README", "README.md", "curriculum", "reports"}
POSITION_LABELS = (
    ("side control", "Side Control (Top)"),
    ("mount", "Mount"),
    ("headquarters", "Headquarters"),
    ("half guard", "Half Guard Top"),
    ("north-south", "North-South"),
    ("north south", "North-South"),
    ("closed guard", "Closed Guard"),
    ("open guard", "Open Guard"),
    ("rear mount", "Rear Mount"),
    ("turtle", "Turtle"),
    ("knee on belly", "Knee On Belly"),
    ("kesa", "Kesa Gatame"),
    ("scarf-hold", "Scarf-Hold"),
    ("scarf hold", "Scarf-Hold"),
)
SUBMISSION_LABELS = (
    ("americana", "Americana"),
    ("armbar", "Armbar"),
    ("triangle", "Triangle"),
    ("rear strangle", "Rear Strangle"),
    ("cross-collar", "Cross-Collar Choke"),
    ("cross collar", "Cross-Collar Choke"),
    ("collar attack", "Collar Attack"),
    ("kimura", "Kimura"),
    ("straight-arm", "Straight Arm"),
    ("straight arm", "Straight Arm"),
    ("footlock", "Footlock"),
)
TAKEDOWN_KEYWORDS = (
    "double leg",
    "body-lock",
    "body lock",
    "inside trip",
    "inside trips",
    "reap",
    "reaps",
    "ouchi",
    "osoto",
    "takedown",
    "throw",
    "shot",
    "go-behind",
    "go behind",
    "mat return",
)
PASSING_KEYWORDS = ("pass", "passing", "knee-cut", "knee cut", "leg drag", "toreando", "headquarters")


def prose(text: str) -> str:
    return text.rstrip().rstrip(".")


def normalize_text(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def slugify(text: str, default: str = "item") -> str:
    parts = re.findall(r"[a-z0-9]+", text.lower())
    return "-".join(parts[:12]) or default


def validate_job_name(job_name: str) -> None:
    if job_name in RESERVED_GENERATED_NAMES:
        raise ValueError(f"reserved generated path: {job_name}")
    if job_name in {".", ".."} or "/" in job_name or "\\" in job_name:
        raise ValueError(f"invalid job name: {job_name}")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", job_name):
        raise ValueError(f"invalid job name: {job_name}")


def build_output_filename(week: dict, output_type: str) -> str:
    week_number = int(week["week"])
    return f"week-{week_number:02d}-{output_type}.md"


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


def build_kb_corpus(repo_root: Path) -> str:
    parts: list[str] = []
    kb_root = repo_root / "kb"
    for path in sorted(kb_root.rglob("*.md")):
        if path.is_file():
            parts.append(normalize_text(path.read_text(encoding="utf-8")))
    return "\n".join(parts)


def extract_candidate_statements(notes_sections: dict[str, str]) -> list[str]:
    statements: list[str] = []
    for section_name in ("Instructions", "Q&A"):
        for line in notes_sections.get(section_name, "").splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                statements.append(stripped[2:].strip())
    return statements


def suggest_kb_target_area(statement: str) -> str:
    normalized = normalize_text(statement)
    if any(token in normalized for token in ("week", "curriculum", "class", "lesson")):
        return "kb/curriculum/"
    if any(token in normalized for token in ("coach", "procedure", "warm up", "warmup", "drill")):
        return "kb/procedures/"
    if "program" in normalized:
        return "kb/programs/"
    return "kb/concepts/"


def build_new_fact_records(repo_root: Path, job_name: str, notes_sections: dict[str, str]) -> list[dict]:
    kb_corpus = build_kb_corpus(repo_root)
    records: list[dict] = []
    seen: set[str] = set()

    for statement in extract_candidate_statements(notes_sections):
        normalized = normalize_text(statement)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        if normalized in kb_corpus:
            continue

        index = len(records) + 1
        records.append(
            {
                "index": index,
                "statement": statement,
                "slug": slugify(statement, default=f"fact-{index:03d}"),
                "suggested_raw_filename": f"job-{job_name}-fact-{index:03d}-{slugify(statement)}.md",
                "suggested_kb_target_area": suggest_kb_target_area(statement),
                "claim_label": "fact",
                "confidence": "0.80",
                "why_new": "No normalized exact-text match was found in the current kb/ pages.",
            }
        )
    return records


def render_new_fact(job_name: str, record: dict) -> str:
    return "\n".join(
        [
            f"# Candidate New Fact {record['index']:03d}",
            "",
            f"- Source Job: {job_name}",
            f"- Claim Label: {record['claim_label']}",
            f"- Confidence: {record['confidence']}",
            f"- Suggested Raw Filename: {record['suggested_raw_filename']}",
            f"- Suggested KB Target Area: {record['suggested_kb_target_area']}",
            "",
            "## Human-Origin Statement",
            record["statement"],
            "",
            "## Why It Appears New",
            record["why_new"],
            "",
        ]
    )


def render_new_facts_index(job_name: str, records: list[dict]) -> str:
    lines = [
        f"# New Facts Review: {job_name}",
        "",
        "This directory contains human-supplied deltas from the job instructions and Q&A that did not match the current `kb/` text.",
        "Review these files manually before promoting any of them into `raw/`.",
        "",
    ]
    if not records:
        lines.append("No candidate new facts were found in this job.")
        lines.append("")
        return "\n".join(lines)

    lines.extend(["## Candidate Facts", ""])
    for record in records:
        filename = f"fact-{record['index']:03d}-{record['slug']}.md"
        lines.append(f"- [{filename}]({filename})")
    lines.append("")
    return "\n".join(lines)


def reset_output_dir(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    return ensure_dir(path)


def copy_reports(repo_root: Path, output_root: Path) -> list[str]:
    copied: list[str] = []
    reports_root = ensure_dir(output_root / "reports")
    source_reports = repo_root / "generated" / "reports"
    for report_path in sorted(source_reports.glob("*.md")):
        destination = reports_root / report_path.name
        shutil.copyfile(report_path, destination)
        copied.append(destination.relative_to(repo_root).as_posix())
    return copied


def write_new_facts(repo_root: Path, output_root: Path, job_name: str, notes_sections: dict[str, str]) -> tuple[list[str], int]:
    new_facts_root = ensure_dir(output_root / "new-facts")
    records = build_new_fact_records(repo_root, job_name, notes_sections)
    output_paths = []
    index_path = new_facts_root / "index.md"
    write_text(index_path, render_new_facts_index(job_name, records), overwrite=True)
    output_paths.append(index_path.relative_to(repo_root).as_posix())
    for record in records:
        filename = f"fact-{record['index']:03d}-{record['slug']}.md"
        fact_path = new_facts_root / filename
        write_text(fact_path, render_new_fact(job_name, record), overwrite=True)
        output_paths.append(fact_path.relative_to(repo_root).as_posix())
    return output_paths, len(records)


def render_metadata_block(program: str, week: dict) -> list[str]:
    lines = [
        "## Metadata",
        f"- Week: {int(week['week']):02d}",
        f"- Cycle: {week.get('cycle', 'unspecified')}",
        f"- Theme: {week.get('theme', 'Not specified')}",
    ]
    if program == "tots":
        lines.extend(
            [
                f"- Movement Theme: {week.get('movement_theme', 'Not specified')}",
                f"- Class Length: {PROGRAM_CONFIG[program]['class_length']}",
            ]
        )
    else:
        lines.extend(
            [
                f"- Teaching Goal: {week.get('teaching_goal', 'Not specified')}",
                f"- Class Length: {PROGRAM_CONFIG[program]['class_length']}",
            ]
        )
    return lines


def render_program_syllabus(program: str, weeks: list[dict]) -> str:
    title = PROGRAM_CONFIG[program]["program_title"]
    lines = [
        f"# {title} Program Syllabus",
        "",
        f"This syllabus maps the {title.lower()} weekly sequence to its cycle, theme, description, and main goal.",
        "",
        "| Week | Cycle | Theme | Description | Main Goal |",
        "| --- | --- | --- | --- | --- |",
    ]

    for week in weeks:
        if program == "tots":
            description = week.get("movement_theme", "Not specified")
            main_goal = week.get("coach_notes", "Not specified")
        else:
            sections = week.get("sections", [])
            description = sections[0].get("focus", "Not specified") if sections else "Not specified"
            main_goal = week.get("teaching_goal", "Not specified")
        lines.append(
            f"| {int(week['week']):02d} | {week.get('cycle', 'unspecified')} | {week.get('theme', 'Not specified')} | {description} | {main_goal} |"
        )

    return "\n".join(lines) + "\n"


def render_youth_or_adult_curriculum(program: str, metadata: dict, week: dict) -> str:
    program_title = PROGRAM_CONFIG[program]["program_title"]
    lines = [
        f"# {program_title} Week {week['week']:02d} Curriculum",
        "",
        *render_metadata_block(program, week),
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
        *render_metadata_block("tots", week),
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
        *render_metadata_block(program, week),
        "",
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
        for section in week.get("sections", []):
            lines.append(f"- {section['name']}: {section.get('focus', 'Not specified')}")
    return "\n".join(lines) + "\n"


def render_coach_guide(program: str, week: dict) -> str:
    lines = [
        f"# {PROGRAM_CONFIG[program]['program_title']} Week {week['week']:02d} Coach Guide",
        "",
        *render_metadata_block(program, week),
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


def first_matching_label(text: str, mapping: tuple[tuple[str, str], ...]) -> str | None:
    normalized = text.lower()
    for needle, label in mapping:
        if needle in normalized:
            return label
    return None


def load_output_examples(job_context: dict, output_type: str) -> list[dict]:
    examples = job_context.get("examples", {})
    if not isinstance(examples, dict):
        return []
    docs = examples.get(output_type, [])
    return docs if isinstance(docs, list) else []


def derive_fully_scripted_style(example_doc: dict) -> dict:
    body = example_doc.get("body", "")
    metadata = example_doc.get("metadata", {})
    lesson_label = str(metadata.get("lesson_label", "Lesson"))
    coaching_label = str(metadata.get("coaching_label", "Coaching tip"))
    level_1_label = str(metadata.get("level_1_label", "L1"))
    level_2_label = str(metadata.get("level_2_label", "L2"))
    outcome_label = str(metadata.get("outcome_label", "Outcome"))
    cla_label = str(metadata.get("cla_label", "CLA/Situational Rolling Options"))

    lesson_match = re.search(r"^##+\s+([^:\n]+):\s+.+$", body, flags=re.MULTILINE)
    if "lesson_label" not in metadata and lesson_match:
        lesson_label = lesson_match.group(1).strip()

    coaching_match = re.search(r"^\s*-\s+(Coaching tip|Cue|Tip):\s+.+$", body, flags=re.MULTILINE)
    if "coaching_label" not in metadata and coaching_match:
        coaching_label = coaching_match.group(1).strip()

    level_1_match = re.search(r"^\s*-\s+(Level 1|L1):\s+.+$", body, flags=re.MULTILINE)
    if "level_1_label" not in metadata and level_1_match:
        level_1_label = level_1_match.group(1).strip()

    level_2_match = re.search(r"^\s*-\s+(Level 2|L2):\s+.+$", body, flags=re.MULTILINE)
    if "level_2_label" not in metadata and level_2_match:
        level_2_label = level_2_match.group(1).strip()

    outcome_match = re.search(r"^\s*-\s+(Outcome):\s+.+$", body, flags=re.MULTILINE)
    if "outcome_label" not in metadata and outcome_match:
        outcome_label = outcome_match.group(1).strip()

    cla_match = re.search(r"^\s*-\s+\*\*([^*\n]+CLA[^*\n]*)\*\*:\s*$", body, flags=re.MULTILINE)
    if "cla_label" not in metadata and cla_match:
        cla_label = cla_match.group(1).strip()

    notes = metadata.get("notes", [])
    if not isinstance(notes, list):
        notes = []

    return {
        "lesson_label": lesson_label,
        "coaching_label": coaching_label,
        "level_1_label": level_1_label,
        "level_2_label": level_2_label,
        "outcome_label": outcome_label,
        "cla_label": cla_label,
        "notes": [str(note) for note in notes],
    }


def should_add_cla_block(style: dict, week: dict, section: dict) -> bool:
    notes_blob = " ".join(style.get("notes", [])).lower()
    if "cla" not in notes_blob and "situational" not in notes_blob and "constraints-led" not in notes_blob:
        return False

    signals = " ".join(
        [
            str(week.get("coach_notes", "")),
            str(week.get("adult_specific_notes", "")),
            str(section.get("coach_notes", "")),
        ]
    ).lower()
    return any(
        token in signals
        for token in ("reaction", "constraint", "round", "rounds", "progressive resistance", "sparring", "live")
    )


def render_cla_block(style: dict, section: dict) -> list[str]:
    focus = prose(section.get("focus", "the primary focus"))
    level_1 = prose(section.get("level_1", "the level 1 action"))
    level_2 = prose(section.get("level_2", "the level 2 action"))
    return [
        f"- **{style['cla_label']}**:",
        f"  - Start from the core position in {focus} and work until {level_1.lower()} or the position resets.",
        f"  - Start from a successful first exchange and continue until {level_2.lower()} or the defender escapes.",
    ]


def semantic_block_title(title: str) -> str:
    return f"- **{title}**"


def render_structured_section_script(week: dict, section: dict) -> list[str]:
    cycle = prose(str(week.get("cycle", "unspecified"))).upper()
    focus = prose(section.get("focus", week.get("theme", "Not specified")))
    coach_tip = prose(section.get("coach_notes", week.get("coach_notes", "Not specified")))
    level_1 = prose(section.get("level_1", "Not specified"))
    level_2 = prose(section.get("level_2", "Not specified"))
    outcome = prose(week.get("teaching_goal", week.get("theme", "Not specified")))

    return [
        f"### Week {int(week['week'])} ({cycle} CYCLE)",
        "",
        f"#### FLOW: {focus}",
        "",
        f"- **{section['name']}**",
        f'  - Coaching tip: "{coach_tip}"',
        f"  - L1: {level_1}",
        f"  - L2: {level_2}",
        f"  - Outcome: {outcome}",
    ]


def derive_semantic_example_blocks(week: dict, section: dict) -> list[dict]:
    combined = " ".join(
        [
            str(week.get("theme", "")),
            str(section.get("focus", "")),
            str(section.get("level_1", "")),
            str(section.get("level_2", "")),
        ]
    ).lower()
    position_label = first_matching_label(combined, POSITION_LABELS)
    submission_label = first_matching_label(combined, SUBMISSION_LABELS)
    has_takedown = any(keyword in combined for keyword in TAKEDOWN_KEYWORDS)
    has_passing = any(keyword in combined for keyword in PASSING_KEYWORDS)
    level_1 = prose(section.get("level_1", "Not specified"))
    level_2 = prose(section.get("level_2", "Not specified"))
    outcome = prose(week.get("teaching_goal", week.get("theme", "Not specified")))

    if has_takedown:
        blocks = [
            {
                "title": "Takedown",
                "lines": [
                    ("level_1", level_1),
                    ("outcome", outcome),
                ],
            }
        ]
        if has_passing:
            blocks.append(
                {
                    "title": "Ground: Passing Finish",
                    "lines": [("level_2", level_2)],
                }
            )
        elif position_label:
            blocks.append(
                {
                    "title": f"Ground: {position_label}",
                    "lines": [("level_2", level_2)],
                }
            )
        return blocks

    if submission_label:
        ground_title = f"Ground: {position_label}" if position_label else "Ground"
        return [
            {
                "title": ground_title,
                "lines": [("level_1", level_1)],
            },
            {
                "title": f"Submission: {submission_label}",
                "lines": [
                    ("level_2", level_2),
                    ("outcome", outcome),
                ],
            },
        ]

    return []


def render_example_driven_section_script(style: dict, week: dict, section: dict) -> list[str]:
    lesson_title = prose(section.get("focus", week.get("theme", "Not specified")))
    coach_tip = prose(section.get("coach_notes", week.get("coach_notes", "Not specified")))
    level_1 = prose(section.get("level_1", "Not specified"))
    level_2 = prose(section.get("level_2", "Not specified"))
    outcome = prose(week.get("teaching_goal", week.get("theme", "Not specified")))
    semantic_blocks = derive_semantic_example_blocks(week, section)

    lines = [
        f"### {style['lesson_label']}: {lesson_title}",
        "",
    ]
    if semantic_blocks:
        for index, block in enumerate(semantic_blocks):
            lines.append(semantic_block_title(block["title"]))
            if index == 0:
                lines.append(f'  - {style["coaching_label"]}: "{coach_tip}"')
            for line_type, value in block["lines"]:
                if line_type == "level_1":
                    lines.append(f"  - {style['level_1_label']}: {value}")
                elif line_type == "level_2":
                    lines.append(f"  - {style['level_2_label']}: {value}")
                elif line_type == "outcome":
                    lines.append(f"  - {style['outcome_label']}: {value}")
            if block is not semantic_blocks[-1]:
                lines.append("")
    else:
        lines.extend(
            [
                f"- **{section['name']}**",
                f'  - {style["coaching_label"]}: "{coach_tip}"',
                f"  - {style['level_1_label']}: {level_1}",
                f"  - {style['level_2_label']}: {level_2}",
                f"  - {style['outcome_label']}: {outcome}",
            ]
        )
    if should_add_cla_block(style, week, section):
        lines.extend(["", *render_cla_block(style, section)])
    return lines


def render_fully_scripted_session(program: str, week: dict, job_context: dict) -> str:
    title = PROGRAM_CONFIG[program]["program_title"]
    fully_scripted_examples = load_output_examples(job_context, "fully-scripted-session")
    example_style = derive_fully_scripted_style(fully_scripted_examples[0]) if fully_scripted_examples else None
    lines = [
        f"# {title} Week {week['week']:02d} Fully Scripted Session",
        "",
        *render_metadata_block(program, week),
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
            section_lines = render_structured_section_script(week, section)
            if example_style:
                section_lines = render_example_driven_section_script(example_style, week, section)
            lines.extend(
                [
                    "",
                    f"## {section['name']} Script",
                    *section_lines,
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


def render_output(program: str, output_type: str, metadata: dict, week: dict, job_context: dict) -> str:
    if output_type == "curriculum":
        return render_curriculum(program, metadata, week)
    if output_type == "quick-outline":
        return render_quick_outline(program, week)
    if output_type == "coach-guide":
        return render_coach_guide(program, week)
    if output_type == "fully-scripted-session":
        return render_fully_scripted_session(program, week, job_context)
    raise ValueError(f"unknown output type: {output_type}")


def generate(repo_root: Path, job_spec: dict, job_context: dict) -> dict:
    job_name = job_context["job_name"]
    validate_job_name(job_name)

    output_root = ensure_dir(repo_root / "generated" / job_name)
    curriculum_root = reset_output_dir(output_root / "curriculum")
    reset_output_dir(output_root / "reports")
    reset_output_dir(output_root / "new-facts")

    output_paths: list[str] = []

    for program in PROGRAM_CONFIG:
        metadata, weeks = load_program_data(repo_root, program)
        output_dir = ensure_dir(curriculum_root / program)
        for week in weeks:
            for output_type in OUTPUT_TYPES:
                filename = build_output_filename(week, output_type)
                content = render_output(program, output_type, metadata, week, job_context)
                output_path = output_dir / filename
                write_text(output_path, content, overwrite=True)
                output_paths.append(output_path.relative_to(repo_root).as_posix())
        syllabus_path = curriculum_root / f"{program}-syllabus.md"
        write_text(syllabus_path, render_program_syllabus(program, weeks), overwrite=True)
        output_paths.append(syllabus_path.relative_to(repo_root).as_posix())

    output_paths.extend(copy_reports(repo_root, output_root))
    new_fact_paths, new_fact_count = write_new_facts(repo_root, output_root, job_name, job_context["notes_sections"])
    output_paths.extend(new_fact_paths)

    return {
        "outputs": sorted(output_paths),
        "warnings": [],
        "new_facts_count": new_fact_count,
        "generator": "curriculum",
    }
