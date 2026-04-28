from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from common import ensure_dir, parse_frontmatter, write_text


PROGRAM_CONFIG = {
    "youth": {
        "legacy_page_path": "kb/curriculum/youth-24-week-theme-map.md",
        "generated_filename": "youth-24-week-theme-map.md",
        "class_length": "60 minutes",
        "program_title": "Youth",
        "default_title": "Youth 24-Week Theme Map",
    },
    "adult": {
        "legacy_page_path": "kb/curriculum/adult-24-week-theme-map.md",
        "generated_filename": "adult-24-week-theme-map.md",
        "class_length": "60 minutes",
        "program_title": "Adult",
        "default_title": "Adult 24-Week Theme Map",
    },
    "tots": {
        "legacy_page_path": "kb/curriculum/tots-12-week-theme-map.md",
        "generated_filename": "tots-12-week-theme-map.md",
        "class_length": "30 minutes",
        "program_title": "Tots",
        "default_title": "Tots 12-Week Theme Map",
    },
}

OUTPUT_TYPES = ("curriculum", "quick-outline", "coach-guide", "fully-scripted-session")
RESERVED_GENERATED_NAMES = {"README", "README.md", "curriculum", "reports"}


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


def load_week_map_page(page_path: Path) -> tuple[str, dict, list[dict]]:
    text = page_path.read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(text)
    payload = extract_json_block(body)
    weeks = payload.get("weeks")
    if not isinstance(weeks, list):
        raise ValueError(f"weeks payload must be a list in {page_path}")
    return text, metadata, weeks


def generated_week_map_path(repo_root: Path, job_name: str, program: str) -> Path:
    return repo_root / "generated" / job_name / "week-maps" / PROGRAM_CONFIG[program]["generated_filename"]


def configured_kb_pages(job_spec: dict) -> list[str]:
    inputs = job_spec.get("inputs", {})
    kb_pages = inputs.get("kb_pages", [])
    if not isinstance(kb_pages, list):
        raise ValueError("job spec inputs.kb_pages must be a list")
    return [str(page) for page in kb_pages]


def source_basis(metadata: dict) -> str:
    source_items = metadata.get("source_refs") or metadata.get("source_kb_pages") or []
    if isinstance(source_items, list):
        return ", ".join(str(item) for item in source_items) or "Not specified"
    return str(source_items) or "Not specified"


def load_bootstrap_week_data(program: str) -> tuple[dict, list[dict]]:
    repo_root = Path(__file__).resolve().parents[1]
    page_path = repo_root / PROGRAM_CONFIG[program]["legacy_page_path"]
    if not page_path.exists():
        raise FileNotFoundError(f"missing bootstrap week map: {page_path}")
    _, metadata, weeks = load_week_map_page(page_path)
    return metadata, weeks


BOOTSTRAP_WEEK_DATA = {program: load_bootstrap_week_data(program) for program in PROGRAM_CONFIG}


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


def render_generated_week_map(program: str, source_kb_pages: list[str], weeks: list[dict], metadata: dict | None = None) -> str:
    metadata = metadata or {}
    title = metadata.get("title", PROGRAM_CONFIG[program]["default_title"])
    page_id = metadata.get("id", f"generated-{program}-week-map")
    confidence = metadata.get("confidence", "0.95")

    source_lines = source_kb_pages or []
    warnings = metadata.get("warnings") or ["none"]
    generation_notes = metadata.get("generation_notes") or ["two-stage curriculum generator artifact"]

    lines = [
        "---",
        f"id: {page_id}",
        "type: generated-curriculum-candidate",
        f'title: "{title}"',
        "status: active",
        "source_kb_pages:",
    ]
    lines.extend(f"  - {page}" for page in source_lines)
    lines.append("generation_notes:")
    lines.extend(f"  - {note}" for note in generation_notes)
    lines.append("warnings:")
    lines.extend(f"  - {warning}" for warning in warnings)
    lines.extend(
        [
            f"confidence: {confidence}",
            "---",
            f"# {title}",
            "",
            f"Candidate week map for {program}.",
            "",
            "```json",
            json.dumps({"weeks": weeks}, indent=2),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def existing_generated_week_map(repo_root: Path, job_name: str, program: str) -> str | None:
    page_path = generated_week_map_path(repo_root, job_name, program)
    if not page_path.exists():
        return None
    return page_path.read_text(encoding="utf-8")


def legacy_week_map_input(job_spec: dict, program: str) -> str | None:
    legacy_path = PROGRAM_CONFIG[program]["legacy_page_path"]
    if legacy_path in configured_kb_pages(job_spec):
        return legacy_path
    return None


def synthesize_program_week_map(repo_root: Path, job_spec: dict, job_context: dict, program: str) -> str:
    existing_text = existing_generated_week_map(repo_root, job_context["job_name"], program)
    if existing_text is not None:
        return existing_text

    legacy_path = legacy_week_map_input(job_spec, program)
    if legacy_path is not None:
        _, metadata, weeks = load_week_map_page(repo_root / legacy_path)
        return render_generated_week_map(
            program,
            [legacy_path],
            weeks,
            metadata={
                "confidence": metadata.get("confidence", "0.95"),
                "generation_notes": ["derived from legacy KB week-map input"],
                "id": metadata.get("id", f"generated-{program}-week-map"),
                "title": metadata.get("title", PROGRAM_CONFIG[program]["default_title"]),
                "warnings": ["none"],
            },
        )

    metadata, weeks = BOOTSTRAP_WEEK_DATA[program]
    return render_generated_week_map(
        program,
        configured_kb_pages(job_spec),
        weeks,
        metadata={
            "confidence": metadata.get("confidence", "0.95"),
            "generation_notes": ["bootstrapped from the framework-stage curriculum baseline"],
            "id": f"generated-{program}-week-map",
            "title": metadata.get("title", PROGRAM_CONFIG[program]["default_title"]),
            "warnings": ["none"],
        },
    )


def write_generated_week_maps(repo_root: Path, job_spec: dict, job_context: dict) -> list[str]:
    output_paths: list[str] = []
    for program in PROGRAM_CONFIG:
        page_path = generated_week_map_path(repo_root, job_context["job_name"], program)
        page_text = synthesize_program_week_map(repo_root, job_spec, job_context, program)
        write_text(page_path, page_text, overwrite=True)
        output_paths.append(page_path.relative_to(repo_root).as_posix())
    return output_paths


def load_generated_program_data(repo_root: Path, job_name: str, program: str) -> tuple[dict, list[dict]]:
    page_path = generated_week_map_path(repo_root, job_name, program)
    if not page_path.exists():
        raise FileNotFoundError(f"missing generated week map: {page_path.relative_to(repo_root).as_posix()}")
    _, metadata, weeks = load_week_map_page(page_path)
    return metadata, weeks


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
        f"- Source Basis: {source_basis(metadata)}",
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
        f"- Source Basis: {source_basis(metadata)}",
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


def render_fully_scripted_session(program: str, week: dict) -> str:
    title = PROGRAM_CONFIG[program]["program_title"]
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


def generate(repo_root: Path, job_spec: dict, job_context: dict) -> dict:
    job_name = job_context["job_name"]
    validate_job_name(job_name)

    output_root = ensure_dir(repo_root / "generated" / job_name)
    curriculum_root = reset_output_dir(output_root / "curriculum")
    reset_output_dir(output_root / "reports")
    reset_output_dir(output_root / "new-facts")

    output_paths: list[str] = []
    output_paths.extend(write_generated_week_maps(repo_root, job_spec, job_context))

    for program in PROGRAM_CONFIG:
        metadata, weeks = load_generated_program_data(repo_root, job_name, program)
        output_dir = ensure_dir(curriculum_root / program)
        for week in weeks:
            for output_type in OUTPUT_TYPES:
                filename = build_output_filename(week, output_type)
                content = render_output(program, output_type, metadata, week)
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
