from __future__ import annotations

import shutil
from pathlib import Path

from common import ensure_dir, parse_frontmatter, write_text


PROGRAM_RULES = {
    "adult": {
        "weeks": 24,
        "class_length": "60 minutes",
        "title": "Adult",
    },
    "youth": {
        "weeks": 24,
        "class_length": "60 minutes",
        "title": "Youth",
    },
    "tots": {
        "weeks": 12,
        "class_length": "30 minutes",
        "title": "Tots",
    },
}

FOUNDATION_THEMES = [
    {
        "theme": "Double Leg to Side Control",
        "takedown": "Double leg entry to a controlled finish on top.",
        "ground": "Side control pin and basic top stabilization.",
        "submission": "Americana or shoulder-isolation finish.",
        "coach_focus": "Connect the shot to top pressure without rushing the finish.",
    },
    {
        "theme": "Sprawl, Go-Behind, and Turtle Control",
        "takedown": "Sprawl reaction to go-behind finish.",
        "ground": "Turtle control and seatbelt awareness.",
        "submission": "Back exposure or turnover win condition.",
        "coach_focus": "Reward defensive reaction and immediate angle changes.",
    },
    {
        "theme": "Single Leg to Knee-On-Belly",
        "takedown": "Single leg finish with strong posture.",
        "ground": "Knee-on-belly stabilization and transitions.",
        "submission": "Straight armbar or mounted transition.",
        "coach_focus": "Keep head position disciplined through the finish.",
    },
    {
        "theme": "Body Lock Entry to Mount",
        "takedown": "Body lock entry with balance-breaking finish.",
        "ground": "Mount retention and pressure.",
        "submission": "Cross-collar or arm-isolation finish.",
        "coach_focus": "Teach pressure through chest connection before advancing.",
    },
    {
        "theme": "Snap Down to Front Headlock",
        "takedown": "Snap down into front headlock control.",
        "ground": "Front headlock to spin-behind top control.",
        "submission": "Guillotine threat or positional conversion.",
        "coach_focus": "Use snaps to create posture reactions, not just speed.",
    },
    {
        "theme": "Inside Trip to Half Guard Top",
        "takedown": "Inside trip with upper-body control.",
        "ground": "Half guard top pressure and crossface discipline.",
        "submission": "Head-and-arm pressure or pass-to-finish sequence.",
        "coach_focus": "Reinforce balance before committing the trip.",
    },
    {
        "theme": "Arm Drag to Rear Body Lock",
        "takedown": "Arm drag to rear angle or mat return.",
        "ground": "Rear control entry and seatbelt management.",
        "submission": "Rear strangle mechanics or back-control win.",
        "coach_focus": "Teach angle creation before grip chasing.",
    },
    {
        "theme": "Collar Tie to Knee Tap",
        "takedown": "Collar tie to knee tap finish.",
        "ground": "Passing off the finish into side control.",
        "submission": "Kimura or top-side attack chain.",
        "coach_focus": "Emphasize head position and connection through the tap.",
    },
    {
        "theme": "Duck Under to Side Control",
        "takedown": "Duck under entry to clean top position.",
        "ground": "Side control switching and pin transitions.",
        "submission": "Americana and transition awareness.",
        "coach_focus": "Use timing and posture, not arm strength.",
    },
    {
        "theme": "Ankle Pick to Mount Path",
        "takedown": "Ankle pick with posture break and angle.",
        "ground": "Mount entry after a clean finish.",
        "submission": "Mounted attack options and retention.",
        "coach_focus": "Keep the pick low and the chest tall.",
    },
    {
        "theme": "Front Headlock to Go-Behind",
        "takedown": "Front headlock snap and spin finish.",
        "ground": "Top control off the go-behind with chest pressure.",
        "submission": "Head-and-arm or back-take transition.",
        "coach_focus": "Hold pressure through the turn, not after it.",
    },
]

ADULT_FINAL_THEMES = [
    {
        "theme": "Lower-Body Entry and Safety",
        "takedown": "Clinch-to-ashi entry with controlled descent.",
        "ground": "Ashi garami positioning and partner safety.",
        "submission": "Straight ankle-lock finishing mechanics under clear limits.",
        "coach_focus": "Teach control, tap awareness, and slow finishing tempo.",
    },
    {
        "theme": "Lower-Body Defense and Exit",
        "takedown": "Entries that end in safe leg-entanglement awareness.",
        "ground": "Boot line protection, hand fighting, and exit routes.",
        "submission": "No new finish; focus on safe recognition and escape.",
        "coach_focus": "Keep this week defensive-first and tightly supervised.",
    },
]

YOUTH_FINAL_THEMES = [
    {
        "theme": "Standing Self-Defence Awareness",
        "takedown": "Safe clinch entry, posture, and balance recovery.",
        "ground": "Top control after a simple finish with quick disengagement.",
        "submission": "No submission emphasis; positional safety win condition.",
        "coach_focus": "Frame the lesson as awareness, distance, and adult help.",
    },
    {
        "theme": "Ground Self-Defence Awareness",
        "takedown": "Technical stand-up pathways and base recovery.",
        "ground": "Pin awareness, framing, and escape to standing.",
        "submission": "No submission emphasis; escape and stand is the win.",
        "coach_focus": "Keep the framing calm, age-appropriate, and non-escalatory.",
    },
]

TOTS_THEMES = [
    ("Mat Rules and Ready Stance", "Bear crawls with freeze command", "Red light, green light stance freezes", "Base, bow-in habits, and personal space"),
    ("Balance and Base", "Crab walks and stop-on-command", "Statue balance game", "Strong base with hands and knees"),
    ("Forward Motion and Brakes", "Jog, sprawl, and pop-up patterns", "Traffic-light level change game", "Safe stop and start habits"),
    ("Rolling and Recovering", "Forward rolls to base", "Treasure roll relay", "Get-up and reset habits"),
    ("Partner Awareness", "Mirror footwork game", "Partner shadow movement", "Respectful distance and listening"),
    ("Push and Pull Balance", "Band-free tug games", "Sumo-circle balance game", "Strong posture with gentle contact"),
    ("Change of Direction", "Shuffle, pivot, and drop steps", "Corner chase game", "Turning hips without falling"),
    ("Level Change and Freeze", "Squat-touch-stand flow", "Coach says level game", "Changing levels safely"),
    ("Top and Bottom Awareness", "Crawl over and under obstacles", "Bridge and belly-turn relay", "Recognizing top, bottom, and reset"),
    ("Pin and Escape Play", "Bridge-and-turn movement warm-up", "Hold-and-escape tag game", "Simple frames and turn-to-knees habit"),
    ("Climb and Control", "Bear crawl obstacle path", "Backpack balance game", "Seatbelt idea without long holds"),
    ("Review and Celebration", "Favorite movement review", "Coach-choice game circuit", "Best habits from the full cycle"),
]

REQUIRED_EXAMPLE_IDS = {
    "double-leg-side-control-americana-example-lesson",
    "tots-week-1-mat-rules-base-ready-stance-example",
}


def archive_and_reset_output_dir(path: Path) -> Path:
    archived_path = path.with_name(f"{path.name}-old")
    if archived_path.exists():
        shutil.rmtree(archived_path)
    if path.exists():
        path.rename(archived_path)
    return ensure_dir(path)


def copy_reports(repo_root: Path, output_root: Path) -> list[str]:
    outputs: list[str] = []
    source_reports = repo_root / "generated" / "reports"
    if not source_reports.exists():
        return outputs

    reports_root = ensure_dir(output_root / "reports")
    for report_path in sorted(source_reports.glob("*.md")):
        destination = reports_root / report_path.name
        shutil.copyfile(report_path, destination)
        outputs.append(destination.relative_to(repo_root).as_posix())
    return outputs


def extract_preserved_example(body: str) -> str:
    marker = "## Preserved Example Format"
    if marker not in body:
        raise ValueError("missing preserved example format section")
    return body.split(marker, 1)[1].strip()


def load_kb_inputs(repo_root: Path, job_spec: dict) -> dict[str, dict]:
    inputs = job_spec.get("inputs", {})
    kb_pages = inputs.get("kb_pages", [])
    if not isinstance(kb_pages, list):
        raise ValueError("job input kb_pages must be a list")

    loaded: dict[str, dict] = {}
    missing_paths: list[str] = []
    missing_example = False

    for relative_path in kb_pages:
        page_path = repo_root / relative_path
        if not page_path.exists():
            missing_paths.append(relative_path)
            if any(example_id in relative_path for example_id in REQUIRED_EXAMPLE_IDS):
                missing_example = True
            continue
        metadata, body = parse_frontmatter(page_path.read_text(encoding="utf-8"))
        page_id = str(metadata.get("id") or page_path.stem)
        loaded[page_id] = {
            "path": relative_path,
            "metadata": metadata,
            "body": body,
        }

    if missing_example:
        raise ValueError("coach lesson plan generation requires example KB pages for adult/youth and tots formatting")
    if missing_paths:
        raise ValueError(f"missing kb page: {missing_paths[0]}")

    return loaded


def validate_required_examples(kb_pages: dict[str, dict]) -> None:
    if "double-leg-side-control-americana-example-lesson" not in kb_pages:
        raise ValueError("coach lesson plan generation requires example KB pages for adult/youth formatting")
    if "tots-week-1-mat-rules-base-ready-stance-example" not in kb_pages:
        raise ValueError("coach lesson plan generation requires example KB pages for tots formatting")

    extract_preserved_example(kb_pages["double-leg-side-control-americana-example-lesson"]["body"])
    extract_preserved_example(kb_pages["tots-week-1-mat-rules-base-ready-stance-example"]["body"])


def extract_section_bullets(body: str, heading: str) -> list[str]:
    lines = body.splitlines()
    target = f"## {heading}"
    capturing = False
    bullets: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == target:
            capturing = True
            continue
        if capturing and stripped.startswith("## "):
            break
        if capturing and stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def bundle_lines(*groups: list[str], limit: int = 3) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for item in group:
            cleaned = " ".join(item.split())
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            lines.append(cleaned)
            if len(lines) >= limit:
                return lines
    return lines


def build_kb_detail_bundle(kb_pages: dict[str, dict]) -> dict[str, list[str]]:
    def body(page_id: str) -> str:
        return kb_pages.get(page_id, {}).get("body", "")

    guard_detailed = extract_section_bullets(body("guard-framework"), "Detailed Notes")
    guard_operational = extract_section_bullets(body("guard-framework"), "Operational Implications")
    escape_detailed = extract_section_bullets(body("escape-framework"), "Detailed Notes")
    warmup_operational = extract_section_bullets(body("movement-and-warmup-framework"), "Operational Implications")
    submission_safety = extract_section_bullets(body("submission-framework"), "Constraints or Safety Notes")
    class_operational = extract_section_bullets(body("class-structure-principles"), "Operational Implications")
    youth_program_operational = extract_section_bullets(body("kids-youth-development-program"), "Operational Implications")
    side_control_detailed = extract_section_bullets(body("side-control-system"), "Detailed Notes")
    situational_detailed = extract_section_bullets(body("example-situational-start-pattern"), "Detailed Notes")
    lesson_delivery = extract_section_bullets(body("technical-lesson-delivery-model"), "Operational Implications")
    warmup_pattern = extract_section_bullets(body("example-lesson-warmup-option-pattern"), "Detailed Notes")

    return {
        "opening_emphasis": bundle_lines(class_operational, lesson_delivery, limit=3),
        "warmup_emphasis": bundle_lines(warmup_operational, warmup_pattern, class_operational, limit=3),
        "defensive_emphasis": bundle_lines(escape_detailed, guard_operational, limit=3),
        "guard_emphasis": bundle_lines(guard_operational, guard_detailed, limit=3),
        "top_control_emphasis": bundle_lines(side_control_detailed, class_operational, limit=3),
        "submission_safety": bundle_lines(submission_safety, limit=3),
        "situational_emphasis": bundle_lines(situational_detailed, class_operational, limit=2),
        "youth_program_framing": bundle_lines(youth_program_operational, limit=3),
        "tots_framing": bundle_lines(warmup_operational, class_operational, youth_program_operational, limit=3),
    }


def build_cycle_label(week_number: int) -> str:
    return "offensive" if ((week_number - 1) // 2) % 2 == 0 else "defensive"


def build_missing_info_prompts(program: str) -> list[str]:
    prompts = [
        "- Preferred class-length adjustment: ____________________",
        "- Specific emphasis or theme rename for this week: ____________________",
    ]
    if program == "adult":
        prompts.append("- Allowed leg-lock depth or restrictions for this group: ____________________")
    elif program == "youth":
        prompts.append("- Preferred self-defence scenario framing for this group: ____________________")
    else:
        prompts.append("- Preferred substitute game if attention is low: ____________________")
    return prompts


def choose_ground_emphasis(week: dict, detail_bundle: dict[str, list[str]]) -> list[str]:
    ground_text = week["ground"].lower()
    if week["cycle"] == "defensive":
        return detail_bundle["defensive_emphasis"]
    if any(keyword in ground_text for keyword in ("side control", "mount", "top control", "knee-on-belly")):
        return detail_bundle["top_control_emphasis"]
    return detail_bundle["guard_emphasis"]


def synthesize_adult_or_youth_week(program: str, week_number: int, detail_bundle: dict[str, list[str]]) -> dict:
    if week_number <= 22:
        basis = FOUNDATION_THEMES[(week_number - 1) % len(FOUNDATION_THEMES)]
    else:
        basis = ADULT_FINAL_THEMES[week_number - 23] if program == "adult" else YOUTH_FINAL_THEMES[week_number - 23]

    theme = basis["theme"] if week_number > 22 else f"{basis['theme']} Fundamentals"
    cycle = build_cycle_label(week_number)
    week = {
        "week": week_number,
        "program": program,
        "cycle": cycle,
        "theme": theme,
        "teaching_goal": f"Build a connected {basis['takedown'].split('.', 1)[0].lower()} into {basis['ground'].split('.', 1)[0].lower()} sequence.",
        "takedown": basis["takedown"],
        "ground": basis["ground"],
        "submission": basis["submission"],
        "coach_focus": basis["coach_focus"],
        "warmup_movement": "Stance, level change, and movement-prep warm-up.",
        "warmup_drill": "Partner entry reps with low resistance and quick resets.",
        "situational": "Start from the target control point and rotate on clear win conditions.",
        "opening_emphasis": detail_bundle["opening_emphasis"],
        "warmup_emphasis": detail_bundle["warmup_emphasis"],
        "ground_emphasis": [],
        "submission_safety": detail_bundle["submission_safety"],
        "situational_emphasis": detail_bundle["situational_emphasis"],
        "program_framing": (
            detail_bundle["youth_program_framing"]
            if program == "youth"
            else ["Use adult pacing and decision-making language.", "Keep decision-making cues clear before pace increases."]
        ),
        "expert_review_notes": [
            "Weekly sequencing is heuristic and should be reviewed before being treated as canonical.",
            "Use the example format as structure, not as proof of exact sequencing.",
        ],
        "kb_gaps": [
            "The KB does not provide a full source-authored 24-week sequence.",
            "Week-specific technique ordering is inferred from examples and general BJJ coaching knowledge.",
        ],
        "missing_info_prompts": build_missing_info_prompts(program),
    }
    week["ground_emphasis"] = choose_ground_emphasis(week, detail_bundle)
    return week


def synthesize_tots_week(week_number: int, detail_bundle: dict[str, list[str]]) -> dict:
    theme, warmup, game, intro = TOTS_THEMES[week_number - 1]
    if week_number <= 4:
        cycle = "foundation"
    elif week_number <= 8:
        cycle = "movement"
    elif week_number <= 11:
        cycle = "partner"
    else:
        cycle = "review"

    return {
        "week": week_number,
        "program": "tots",
        "cycle": cycle,
        "theme": theme,
        "teaching_goal": "Build fun, attention, athletic movement, and comfort on the mat.",
        "warmup": warmup,
        "game": game,
        "intro_grappling": intro,
        "coach_focus": "Keep the pace playful, the instructions short, and the praise immediate.",
        "warmup_emphasis": detail_bundle["warmup_emphasis"],
        "program_framing": detail_bundle["tots_framing"],
        "expert_review_notes": [
            "The tots sequence is heuristic and movement-led rather than source-authored week sequencing.",
        ],
        "kb_gaps": [
            "The KB includes one tots example format but not a complete 12-week authored progression.",
        ],
        "missing_info_prompts": build_missing_info_prompts("tots"),
    }


def synthesize_program_weeks(kb_pages: dict[str, dict]) -> dict[str, list[dict]]:
    validate_required_examples(kb_pages)
    detail_bundle = build_kb_detail_bundle(kb_pages)
    program_weeks = {
        "adult": [synthesize_adult_or_youth_week("adult", week, detail_bundle) for week in range(1, 25)],
        "youth": [synthesize_adult_or_youth_week("youth", week, detail_bundle) for week in range(1, 25)],
        "tots": [synthesize_tots_week(week, detail_bundle) for week in range(1, 13)],
    }
    validate_program_weeks(program_weeks)
    return program_weeks


def validate_program_weeks(program_weeks: dict[str, list[dict]]) -> None:
    if len(program_weeks["adult"]) != PROGRAM_RULES["adult"]["weeks"]:
        raise ValueError("adult coach lesson plans require 24 weeks")
    if len(program_weeks["youth"]) != PROGRAM_RULES["youth"]["weeks"]:
        raise ValueError("youth coach lesson plans require 24 weeks")
    if len(program_weeks["tots"]) != PROGRAM_RULES["tots"]["weeks"]:
        raise ValueError("tots coach lesson plans require 12 weeks")


def render_syllabus(program: str, weeks: list[dict]) -> str:
    title = PROGRAM_RULES[program]["title"]
    lines = [
        f"# {title} Syllabus",
        "",
        f"This syllabus maps the {title.lower()} weekly sequence to its cycle, theme, and main goal.",
        "",
        "| Week | Cycle | Theme | Main Goal |",
        "| --- | --- | --- | --- |",
    ]
    for week in weeks:
        lines.append(f"| {week['week']:02d} | {week['cycle']} | {week['theme']} | {week['teaching_goal']} |")

    lines.append("")
    return "\n".join(lines)


def render_adult_or_youth_lesson_blocks(week: dict) -> list[str]:
    ground_label = week["ground"].split(".", 1)[0]
    submission_label = week["submission"].split(".", 1)[0]
    blocks = [
        "- **Takedown**",
        f"  - Coaching Tip: {week['coach_focus']}",
        f"  - Level 1: {week['takedown']}",
        "  - Level 2: Add timing, angle change, or chain-attack follow-up without increasing chaos.",
        f"  - Outcome: Finish to a clean top position that leads into {ground_label.lower()}",
        f"- **Ground: {ground_label}**",
        f"  - Secure: {week['ground']}",
        "  - Level 2: Add a simple transition or pressure-retention task before the finish.",
        *[f"  - Coaching Emphasis: {item}" for item in week["ground_emphasis"]],
    ]
    if week["cycle"] == "offensive":
        blocks.extend(
            [
                f"- **Submission: {submission_label}**",
                f"  - Cue: {week['submission']}",
                *[f"  - Safety: {item}" for item in week["submission_safety"]],
            ]
        )
    blocks.extend(
        [
            "- **Situational Options**",
            f"  - {week['situational']}",
            *[f"  - Coaching Emphasis: {item}" for item in week["situational_emphasis"]],
            "  - Run short rounds with a fast reset after the first clean win condition or escape.",
        ]
    )
    return blocks


def render_adult_or_youth_lesson(week: dict) -> str:
    return "\n".join(
        [
            f"# Week {week['week']} ({week['cycle'].title()} Cycle)",
            f"- Theme: {week['theme']}",
            f"- Teaching Goal: {week['teaching_goal']}",
            f"- Class Length: {PROGRAM_RULES[week['program']]['class_length']}",
            "",
            "## Opening Script",
            f"- Theme setup: {week['theme']}.",
            f"- Main goal: {week['teaching_goal']}",
            "- Connect the feet-to-floor entry to stable control before chasing pace or extra variation.",
            *[f"- Emphasis: {item}" for item in week["opening_emphasis"]],
            "",
            "## Warm-Up Options",
            "- **Movement Based**",
            f"  - {week['warmup_movement']}",
            *[f"  - Coaching Emphasis: {item}" for item in week["warmup_emphasis"]],
            "- **Drill Based**",
            f"  - {week['warmup_drill']}",
            "  - Keep the reps short, clean, and easy to reset.",
            "",
            f"## Lesson: {week['theme']}",
            *render_adult_or_youth_lesson_blocks(week),
            "",
            "## Coach Notes",
            *[f"- {item}" for item in week["program_framing"]],
            f"- {week['coach_focus']}",
            "- Keep the room moving with short explanation windows and clear reset points.",
            "",
            "## Closing Script",
            f"- Recap the theme: {week['theme']}.",
            "- Call out one technical habit and one safety habit that showed up well in the room.",
            "- Reinforce one cue that students can carry into the next week of the cycle.",
            "",
        ]
    )


def render_tots_lesson(week: dict) -> str:
    return "\n".join(
        [
            f"# Week {week['week']} ({week['cycle'].title()})",
            f"Theme: {week['theme']}",
            f"Teaching Goal: {week['teaching_goal']}",
            f"Class Length: {PROGRAM_RULES['tots']['class_length']}",
            "",
            "## Lesson",
            "### Introduce the Theme",
            f"- Tell the class the goal is {week['theme']}.",
            *[f"- Coaching Emphasis: {item}" for item in week["program_framing"][:2]],
            "",
            "### Warm-Up Block",
            f"- {week['warmup']}",
            *[f"- Coaching Emphasis: {item}" for item in week["warmup_emphasis"][:2]],
            "",
            "### Main Activity Block",
            f"- {week['game']}",
            "- Keep the game moving quickly and stop before attention drops.",
            "",
            "### Intro Grappling Block",
            f"- {week['intro_grappling']}",
            "- Keep contact gentle and reset early when posture breaks.",
            "",
            "### Coach Notes",
            f"- {week['coach_focus']}",
            "- Keep transitions short and celebrate good listening quickly.",
            *[f"- Coaching Emphasis: {item}" for item in week["program_framing"][2:3]],
            "",
            "### Closing Script",
            "- Recap the theme, praise the best example from the room, and finish with a clear dismissal.",
            "",
        ]
    )


def render_kb_grounding(week: dict, kb_pages: dict[str, dict]) -> str:
    supporting_paths = [entry["path"] for entry in kb_pages.values()]
    direct_support = [
        "- Preserved lesson-format examples provide the markdown shape for the lesson file.",
        "- Guard, escape, submission, class-structure, and lesson-delivery KB pages provide coaching detail for openings, warm-ups, technical emphasis, and safety notes.",
    ]
    inferred_support = [
        f"- The exact week-{week['week']:02d} sequence for {week['program']} is heuristic rather than source-authored.",
        "- Theme wording, week ordering, and detailed technical pairings were synthesized from general coaching knowledge.",
    ]

    lines = [
        f"# Week {week['week']:02d} KB Grounding",
        "",
        "## KB-Grounded Inputs",
        *direct_support,
        "",
        "## Inferred Content",
        *inferred_support,
        "",
        "## Weak Support",
        *[f"- {item}" for item in week["kb_gaps"]],
        "",
        "## Source Pages",
        *[f"- {path}" for path in supporting_paths],
        "",
    ]
    return "\n".join(lines)


def render_program_missing_info(program: str, weeks: list[dict]) -> str:
    shared_gaps: list[str] = []
    shared_seen: set[str] = set()
    reviewer_notes: list[str] = []
    reviewer_seen: set[str] = set()
    lines = [
        f"# {PROGRAM_RULES[program]['title']} Missing Information",
        "",
        "## Shared Gaps",
    ]

    for week in weeks:
        for gap in week["kb_gaps"]:
            if gap not in shared_seen:
                shared_seen.add(gap)
                shared_gaps.append(gap)
        for note in week["expert_review_notes"]:
            if note not in reviewer_seen:
                reviewer_seen.add(note)
                reviewer_notes.append(note)

    lines.extend([f"- {gap}" for gap in shared_gaps])
    lines.extend(["", "## Week-Specific Decisions"])

    for week in weeks:
        lines.extend(
            [
                f"### Week {week['week']:02d}: {week['theme']}",
                *week["missing_info_prompts"],
                "",
            ]
        )

    lines.extend(["## Reviewer Notes", *[f"- {note}" for note in reviewer_notes], ""])
    return "\n".join(lines)


def generate(repo_root: Path, job_spec: dict, job_context: dict) -> dict:
    output_root = archive_and_reset_output_dir(repo_root / "generated" / job_context["job_name"])
    lesson_root = ensure_dir(output_root / "lesson")
    meta_root = ensure_dir(output_root / "meta")

    kb_pages = load_kb_inputs(repo_root, job_spec)
    program_weeks = synthesize_program_weeks(kb_pages)

    outputs: list[str] = []
    warnings = [
        "Lesson sequencing is heuristic and should be reviewed before being treated as canonical.",
        "Coach-facing files preserve the example format, but meta files carry the provenance burden.",
    ]

    for program, weeks in program_weeks.items():
        syllabus_path = lesson_root / f"{program}-syllabus.md"
        write_text(syllabus_path, render_syllabus(program, weeks), overwrite=True)
        outputs.append(syllabus_path.relative_to(repo_root).as_posix())

        missing_info_path = meta_root / program / "missing-info.md"
        write_text(missing_info_path, render_program_missing_info(program, weeks), overwrite=True)
        outputs.append(missing_info_path.relative_to(repo_root).as_posix())

        for week in weeks:
            lesson_path = lesson_root / program / f"week-{week['week']:02d}-lesson-plan.md"
            grounding_path = meta_root / program / f"week-{week['week']:02d}-kb-grounding.md"

            lesson_text = render_tots_lesson(week) if program == "tots" else render_adult_or_youth_lesson(week)
            write_text(lesson_path, lesson_text, overwrite=True)
            write_text(grounding_path, render_kb_grounding(week, kb_pages), overwrite=True)

            outputs.extend(
                [
                    lesson_path.relative_to(repo_root).as_posix(),
                    grounding_path.relative_to(repo_root).as_posix(),
                ]
            )

    if job_spec.get("options", {}).get("include_reports"):
        outputs.extend(copy_reports(repo_root, output_root))

    return {
        "outputs": outputs,
        "warnings": warnings,
        "new_facts_count": 0,
    }
