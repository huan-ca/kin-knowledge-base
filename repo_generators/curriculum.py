from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from common import ensure_dir, parse_frontmatter, write_text


PROGRAM_CONFIG = {
    "youth": {
        "generated_filename": "youth-24-week-theme-map.md",
        "class_length": "60 minutes",
        "program_title": "Youth",
        "default_title": "Youth 24-Week Theme Map",
        "primary_framework_page": "kb/curriculum/youth-24-week-curriculum-framework.md",
        "required_kb_pages": (
            "kb/curriculum/curriculum-week-design-rules.md",
            "kb/curriculum/youth-24-week-curriculum-framework.md",
            "kb/curriculum/groundwork-cycle-framework.md",
            "kb/curriculum/takedown-framework.md",
            "kb/curriculum/takedown-progression-framework.md",
            "kb/curriculum/youth-submission-safety-framework.md",
        ),
    },
    "adult": {
        "generated_filename": "adult-24-week-theme-map.md",
        "class_length": "60 minutes",
        "program_title": "Adult",
        "default_title": "Adult 24-Week Theme Map",
        "primary_framework_page": "kb/curriculum/adult-24-week-curriculum-framework.md",
        "required_kb_pages": (
            "kb/curriculum/curriculum-week-design-rules.md",
            "kb/curriculum/adult-24-week-curriculum-framework.md",
            "kb/curriculum/groundwork-cycle-framework.md",
            "kb/curriculum/takedown-framework.md",
            "kb/curriculum/takedown-progression-framework.md",
            "kb/curriculum/ibjjf-leg-lock-curriculum.md",
        ),
    },
    "tots": {
        "generated_filename": "tots-12-week-theme-map.md",
        "class_length": "30 minutes",
        "program_title": "Tots",
        "default_title": "Tots 12-Week Theme Map",
        "primary_framework_page": "kb/curriculum/tots-12-week-curriculum-framework.md",
        "required_kb_pages": (
            "kb/curriculum/tots-12-week-curriculum-framework.md",
            "kb/concepts/movement-and-warmup-framework.md",
            "kb/concepts/general-physical-preparedness-framework.md",
        ),
    },
}

OUTPUT_TYPES = ("curriculum", "quick-outline", "coach-guide", "fully-scripted-session")
RESERVED_GENERATED_NAMES = {"README", "README.md", "curriculum", "reports"}
REVIEW_STATUS = "heuristic candidate"

OFFENSIVE_VARIANTS = (
    {
        "title": "Foundations",
        "focus_suffix": "Build the first clean landing and control connection before adding pace.",
        "coach_suffix": "Keep the pace cooperative enough that the takedown still lands in the intended ground theme.",
        "review_note": "Confirm the foundation week should precede the chain week for this theme.",
        "level_1_suffix": "Stay with one clean entry and one stable control or finish.",
        "level_2_suffix": "Add one reaction or secondary attack without changing the core problem.",
    },
    {
        "title": "Reactions and Chains",
        "focus_suffix": "Layer the clearest second reaction once the base exchange is stable.",
        "coach_suffix": "Do not add the second layer until the first exchange still looks match-connected.",
        "review_note": "Confirm the chain choices match the gym's preferred compendium vocabulary.",
        "level_1_suffix": "Keep the first exchange intact under light resistance.",
        "level_2_suffix": "Add timing, chaining, or a second finish while preserving the same landing logic.",
    },
)

DEFENSIVE_VARIANTS = (
    {
        "title": "Initial Survival",
        "focus_suffix": "Start with the first safe response and the earliest reliable exit.",
        "coach_suffix": "Reward survival mechanics before asking for fast reversals or counters.",
        "review_note": "Confirm the first-response choice matches the room's current defensive priorities.",
        "level_1_suffix": "Protect posture, frames, and one reliable recovery path.",
        "level_2_suffix": "Add a clean reversal or return-to-neutral option after the first exit works.",
    },
    {
        "title": "Recovery and Counters",
        "focus_suffix": "Recover position first, then add the cleanest counter window or stand-up.",
        "coach_suffix": "Do not let the room chase counters before the recovery mechanics stay safe.",
        "review_note": "Confirm the counter window is age- and room-appropriate for this program.",
        "level_1_suffix": "Recover the safer position without rushing the finish.",
        "level_2_suffix": "Add the best counterattack or stand-up once recovery timing is consistent.",
    },
)

YOUTH_PAIR_SPECS = (
    {
        "cycle": "offensive",
        "theme": "Closed Guard Offense",
        "focus_core": "Teach youth students to connect the standing entry to closed-guard attack ideas.",
        "takedown": "Judo foot sweep entries that clarify how the exchange can settle into closed-guard work.",
        "ground": "Closed guard posture breaks, angle creation, and sweep-or-attack decisions.",
        "submission": "Straight armbar and kimura chains taught with youth-safe pacing and clear tap habits.",
        "coach_notes": "Keep the standing entry simple so the class still spends most of the week inside the ground theme.",
        "level_1": "Build the posture break, one angle change, and one clean finish or sweep.",
        "level_2": "Add a second attack that appears only after posture is broken correctly.",
    },
    {
        "cycle": "defensive",
        "theme": "Mount Escape Layers",
        "focus_core": "Show how a bad landing after a takedown becomes a mount-survival problem that still has structure.",
        "takedown": "Body-lock and snap-down finishes that explain how students can end underneath mount if the exchange goes wrong.",
        "ground": "Bridge, elbow-knee, and safe guard-recovery stages from mount.",
        "submission": "No dedicated finish; the week stays focused on survival, recovery, and controlled reversal choices.",
        "coach_notes": "Keep students from racing to reversals before they can hold frames and survive the first pressure.",
        "level_1": "Protect elbows, bridge at the right time, and recover half guard or closed guard.",
        "level_2": "Add the cleanest reversal or technical stand-up after the first escape route is stable.",
    },
    {
        "cycle": "offensive",
        "theme": "Passing To Control",
        "focus_core": "Link a successful standing finish to the first dependable guard-passing path.",
        "takedown": "Single-leg finishes that land in headquarters, half guard top, or knee-cut starting shapes.",
        "ground": "Toreando and knee-cut passing entries that settle into real side-control pressure.",
        "submission": "Cross-collar, americana, or far-side arm attacks only after the pass becomes stable.",
        "coach_notes": "Make the pass the center of the week instead of turning the takedown into a separate class.",
        "level_1": "Finish the takedown into one pass and one stable pin.",
        "level_2": "Add the best re-route when the first pass is blocked.",
    },
    {
        "cycle": "defensive",
        "theme": "Side Control Recovery",
        "focus_core": "Treat side control as the next defensive layer once the pass gets through.",
        "takedown": "Hip-throw and body-lock examples that let coaches explain how control can settle into side control.",
        "ground": "Frames, hip escape timing, and guard recovery from side control.",
        "submission": "No dedicated finish; the priority is guard recovery, back-to-knees movement, and partner safety.",
        "coach_notes": "Keep the room disciplined about frame quality before adding scrambles.",
        "level_1": "Build the near-side frame, hip movement, and one reliable guard recovery.",
        "level_2": "Add a second recovery route or a clean wrestle-up after the first frame wins space.",
    },
    {
        "cycle": "offensive",
        "theme": "Back Control Attacks",
        "focus_core": "Use the standing exchange to arrive at the back and teach immediate back-control offense.",
        "takedown": "Duck-under, drag, and rear-angle finishes that naturally expose the back.",
        "ground": "Seatbelt control, hooks, and back-maintenance decisions once the position is won.",
        "submission": "Rear naked choke and safe collar-based follow-ups taught as direct back-control extensions.",
        "coach_notes": "Insist on seatbelt and control first so the back week does not become a scramble-only week.",
        "level_1": "Secure seatbelt, stabilize the back, and finish with one simple attack.",
        "level_2": "Add a trap or recovery route when the partner starts peeling grips or hiding the neck.",
    },
    {
        "cycle": "defensive",
        "theme": "Turtle And Front Headlock Recovery",
        "focus_core": "Treat turtle as a real defensive staging area instead of a panic position.",
        "takedown": "Snap-down and front-headlock examples that show why students need structured turtle responses.",
        "ground": "Turtle posture, peek-out timing, safe sit-outs, and front-headlock defense.",
        "submission": "No dedicated finish; the week prioritizes back exposure prevention and clean returns to guard or standing.",
        "coach_notes": "Do not let students dive into rolls before they can protect the neck and manage grips.",
        "level_1": "Protect the neck, win posture, and recover guard or stand up.",
        "level_2": "Add the best sit-out, peek-out, or re-attack once the basic posture is safe.",
    },
    {
        "cycle": "offensive",
        "theme": "Half Guard Top Pressure",
        "focus_core": "Keep match-like pressure on top while converting takedown landings into half-guard offense.",
        "takedown": "Double-leg and body-lock finishes that often settle into half-guard top scenarios.",
        "ground": "Crossfaces, underhooks, and passing pressure from top half guard.",
        "submission": "Kimura, arm-triangle, or backstep follow-ups that stay attached to top-half pressure.",
        "coach_notes": "Reward chest-to-chest pressure and head position before asking for advanced passing changes.",
        "level_1": "Win the underhook, flatten the partner, and complete one reliable pass.",
        "level_2": "Add a backstep, knee-cut continuation, or direct submission threat off the same pressure.",
    },
    {
        "cycle": "defensive",
        "theme": "Half Guard Bottom Recovery",
        "focus_core": "Show how half guard can be a defensive checkpoint rather than a dead stop.",
        "takedown": "Ankle-pick and scramble examples that explain why half guard appears after incomplete finishes.",
        "ground": "Frames, underhook races, knee shield recovery, and stand-up options from bottom half guard.",
        "submission": "No dedicated finish; the week emphasizes recovery, wrestle-up timing, and safe reversals.",
        "coach_notes": "Protect the underhook battle and posture before adding aggressive come-up sequences.",
        "level_1": "Build the knee shield or inside frame and recover a safer guard.",
        "level_2": "Add a wrestle-up, sweep, or stand-up once the first frame is dependable.",
    },
    {
        "cycle": "offensive",
        "theme": "Pin Attack Progression",
        "focus_core": "Turn a completed takedown or pass into immediate attacking pressure from secure pins.",
        "takedown": "Clinch finishes that settle directly into pins or quick transitions through side control.",
        "ground": "Mount, knee-on-belly, and side-control attack chains that stay connected.",
        "submission": "Americana, straight armbar, and collar-based finishes that grow from stable pins.",
        "coach_notes": "Keep the pin quality high so students understand that control creates the finish window.",
        "level_1": "Secure the pin and finish with one direct attack.",
        "level_2": "Add the next attack when the partner's first defense appears.",
    },
    {
        "cycle": "defensive",
        "theme": "Open Guard Retention",
        "focus_core": "Treat open guard as a defensive system that reconnects the student to offense later.",
        "takedown": "Collar-tie, drag, and shot examples that help coaches explain why distance management matters after standing exchanges.",
        "ground": "Hip movement, shin-to-shin, hooks, and frames that rebuild open guard.",
        "submission": "No dedicated finish; the week stays with retention, off-balancing, and safe returns to stronger guard shapes.",
        "coach_notes": "Protect the frame-and-angle battle before chasing sweeps.",
        "level_1": "Recover feet and frames to stop the pass and rebuild distance.",
        "level_2": "Add one off-balance, wrestle-up, or re-guard chain after retention is stable.",
    },
    {
        "cycle": "offensive",
        "theme": "Standing To Top Chains",
        "focus_core": "Use the late-cycle weeks to tie together takedown reactions and top-position continuation.",
        "takedown": "Rear takedowns, Russian ties, and snap-to-go-behind chains that reward connection between standing and top control.",
        "ground": "Immediate passing, pinning, and top-transition choices after the takedown succeeds.",
        "submission": "Coach-selected safe finishes that emerge only after top control becomes stable.",
        "coach_notes": "Treat the week as a connection week, not as a loose collection of unrelated moves.",
        "level_1": "Hit one clean takedown-to-top pathway and stabilize the first pin.",
        "level_2": "Add the clearest follow-up pass or submission when the opponent reacts.",
    },
    {
        "cycle": "defensive",
        "theme": "Standing To Ground Problem Solving",
        "focus_core": "Close the cycle with defensive problem solving that still respects the standing-to-ground connection.",
        "takedown": "Coach-selected review entries from earlier families used to test recovery habits under mild unpredictability.",
        "ground": "Review the clearest escape, recovery, and stand-up patterns from mount, side control, and open guard.",
        "submission": "No dedicated finish; use the week to confirm defensive understanding and safe return paths.",
        "coach_notes": "Keep the density lighter than a pure review dump and stay honest about what still needs expert sequencing changes.",
        "level_1": "Show the safest answer to the most common bad landings and recoveries.",
        "level_2": "Add one counter or stand-up only after the first recovery choice is reliable.",
    },
)

ADULT_PAIR_SPECS = YOUTH_PAIR_SPECS[:-1] + (
    {
        "cycle": "special",
        "theme": "Lower-Body Awareness",
        "focus_core": "Reserve the final adult pair for lower-body offense and defense with explicit safety and rules awareness.",
        "takedown": "Entries that arrive in seated, split-squat, or leg-pummel situations without pretending the exact leg-lock syllabus is source-authored.",
        "ground": "Ashi entries, leg-pummel awareness, and safe early-leg-entanglement decisions.",
        "submission": "Straight ankle lock offense in the first week, then defensive clearing, turning direction, and legal guardrails in the second.",
        "coach_notes": "Make the safety language explicit and keep the room inside the approved rules-aware scope.",
        "level_1": "Build the safest legal entry and the earliest defensive exit.",
        "level_2": "Add controlled secondary entries, counters, or legal finishing pressure only after the room is calm.",
    },
)

TOTS_WEEK_SPECS = (
    {
        "cycle": "foundation",
        "theme": "Base, Balance, and Breakfalls",
        "movement_theme": "Base drills, balance games, and beginner breakfall shapes.",
        "game": "Balance islands and safe-fall relay.",
        "coordination_focus": "Balance, posture, and safe mat contact.",
        "bjj_exposure": "Learning how to stand, sit, and fall safely on the mat.",
        "coach_notes": "Keep explanations short and celebrate every clean reset.",
    },
    {
        "cycle": "foundation",
        "theme": "Bridge and Shrimp Movement",
        "movement_theme": "Bridging, shrimping, and hip movement in straight lines and simple turns.",
        "game": "Bridge tunnel race and shrimp tag.",
        "coordination_focus": "Core control, hip drive, and direction changes.",
        "bjj_exposure": "Feeling how bridge and shrimp motions help when someone is on top.",
        "coach_notes": "Stay game-heavy and do not over-explain the grappling reason yet.",
    },
    {
        "cycle": "foundation",
        "theme": "Sit-Out and Turn-In Reactions",
        "movement_theme": "Sit-outs, turn-ins, and belly-down to base transitions.",
        "game": "Turn-and-tag scramble game.",
        "coordination_focus": "Body rotation and posting hands safely.",
        "bjj_exposure": "Simple escape-style movement without heavy pressure.",
        "coach_notes": "Use lots of demos and reset quickly when attention drops.",
    },
    {
        "cycle": "foundation",
        "theme": "Technical Stand-Up Habits",
        "movement_theme": "Technical stand-up, base switches, and get-up races.",
        "game": "Treasure get-up relay.",
        "coordination_focus": "Hand-foot coordination and staying balanced while standing.",
        "bjj_exposure": "Standing up safely after being on the ground.",
        "coach_notes": "Short reps work better than long lines for this age group.",
    },
    {
        "cycle": "movement",
        "theme": "Grip Fighting and Inside Position",
        "movement_theme": "Grip games, hand-fighting, and inside-position pummeling.",
        "game": "Inside-track hand battle.",
        "coordination_focus": "Hand speed, posture, and staying square.",
        "bjj_exposure": "How to make first contact with a partner without roughness.",
        "coach_notes": "Keep contact playful and supervised so the room stays calm.",
    },
    {
        "cycle": "movement",
        "theme": "Guard Shape and Hooks",
        "movement_theme": "Guard drills, hooks, feet-on-hips shapes, and rolling entries.",
        "game": "Guard monster feet game.",
        "coordination_focus": "Hip mobility and keeping knees, feet, and hands organized.",
        "bjj_exposure": "Feeling what it means to use the legs to manage space.",
        "coach_notes": "Treat this as movement first and technique second.",
    },
    {
        "cycle": "movement",
        "theme": "Scramble and Stand-Up Confidence",
        "movement_theme": "Short scramble drills, stand-ups, and directional changes.",
        "game": "Cone scramble and freeze game.",
        "coordination_focus": "Agility, reorientation, and safe posting.",
        "bjj_exposure": "Getting up and turning back toward the partner safely.",
        "coach_notes": "Keep the rounds very short so quality stays high.",
    },
    {
        "cycle": "movement",
        "theme": "Push-Pull Takedown Games",
        "movement_theme": "Partner push-pull games, off-balancing, and safe entry steps.",
        "game": "Push-pull sumo circles.",
        "coordination_focus": "Posture, balance recovery, and directional force.",
        "bjj_exposure": "Basic off-balancing without hard finishes.",
        "coach_notes": "The goal is confidence and movement quality, not real takedown intensity.",
    },
    {
        "cycle": "partner",
        "theme": "Top and Bottom Awareness",
        "movement_theme": "Partner rotations between top, bottom, and side-to-side movement.",
        "game": "Top-bottom switch relay.",
        "coordination_focus": "Listening, reacting, and changing levels safely.",
        "bjj_exposure": "Learning that top and bottom each have jobs and cues.",
        "coach_notes": "Use clear start-stop rules so transitions stay controlled.",
    },
    {
        "cycle": "partner",
        "theme": "Pass Around the Legs",
        "movement_theme": "Circle-walking, hand-posting, and leg-navigation movement.",
        "game": "Pass the gate game.",
        "coordination_focus": "Footwork, hand placement, and spatial awareness.",
        "bjj_exposure": "Simple ideas for moving around the legs without heavy pressure.",
        "coach_notes": "Keep the skill tiny and the game large.",
    },
    {
        "cycle": "partner",
        "theme": "Hold, Hug, and Stay Safe",
        "movement_theme": "Body-lock shapes, shoulder pressure awareness, and safe hugs around the torso.",
        "game": "Bear-hug balance game.",
        "coordination_focus": "Connection, posture, and cooperative resistance.",
        "bjj_exposure": "Feeling chest-to-chest control without adding technical density.",
        "coach_notes": "Reward gentle control and quick coach-response behavior.",
    },
    {
        "cycle": "review",
        "theme": "Favorite Games and Mat Confidence Review",
        "movement_theme": "Coach-selected review of the strongest movement patterns from the first eleven weeks.",
        "game": "Favorite game review circuit.",
        "coordination_focus": "Confidence, recall, and smooth transitions between activities.",
        "bjj_exposure": "Simple review of top, bottom, and standing comfort on the mat.",
        "coach_notes": "Use this lighter week to observe what needs a future expert rewrite or local adjustment.",
    },
)


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

def read_kb_page(repo_root: Path, relative_path: str) -> tuple[dict, str]:
    page_path = repo_root / relative_path
    if not page_path.exists():
        raise ValueError(f"missing required framework page: {relative_path}")
    text = page_path.read_text(encoding="utf-8")
    return parse_frontmatter(text)


def unique_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for item in items:
        stripped = str(item).strip()
        if not stripped or stripped in seen:
            continue
        seen.add(stripped)
        values.append(stripped)
    return values


def extract_markdown_bullets(body: str, heading: str) -> list[str]:
    target = f"## {heading}"
    bullets: list[str] = []
    active = False
    for raw_line in body.splitlines():
        stripped = raw_line.strip()
        if stripped == target:
            active = True
            continue
        if active and stripped.startswith("## "):
            break
        if active and stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def float_confidence(value: object, default: float = 0.7) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def framework_gap_refs(framework_pages: dict[str, tuple[dict, str]], *, limit: int | None = None) -> list[str]:
    refs: list[str] = []
    for relative_path, (_metadata, body) in framework_pages.items():
        page_name = Path(relative_path).name
        for bullet in extract_markdown_bullets(body, "Gaps"):
            refs.append(f"{page_name}: {bullet}")
    refs = unique_strings(refs)
    return refs if limit is None else refs[:limit]


def heuristic_confidence(framework_pages: dict[str, tuple[dict, str]]) -> str:
    confidences = [float_confidence(metadata.get("confidence")) for metadata, _body in framework_pages.values()]
    if not confidences:
        return "0.50"
    adjusted = max(0.35, min(0.85, (sum(confidences) / len(confidences)) - 0.18))
    return f"{adjusted:.2f}"


def adult_cycle_for_week(week_number: int, default_cycle: str) -> str:
    if week_number == 23:
        return "offensive"
    if week_number == 24:
        return "defensive"
    return default_cycle


def build_pair_review_notes(program: str, theme: str, week_number: int, variant_note: str) -> list[str]:
    notes = [
        f"Confirm that {theme.lower()} belongs in week {week_number} for the {program} room.",
        variant_note,
        "Replace this heuristic pairing if a source-authored calendar is later approved.",
    ]
    if program == "youth":
        notes.append("Confirm youth submission choices stay appropriate for the target age and belt mix.")
    if program == "adult" and week_number >= 23:
        notes.append("Confirm adult lower-body scope, legality, and safety language before live rounds.")
    if program == "tots":
        notes.append("Replace movement or game names with house vocabulary if the coaching team prefers different phrasing.")
    return unique_strings(notes)


def build_week_kb_gaps(program: str, week_number: int, shared_gap_refs: list[str]) -> list[str]:
    gaps = list(shared_gap_refs[:2])
    if program == "youth":
        gaps.append("Youth legality and progression rules are summarized in the KB, but a full age-by-belt matrix is still missing.")
    if program == "adult" and week_number >= 23:
        gaps.append("The KB reserves adult lower-body focus for the last two weeks, but exact week-by-week leg-lock sequencing remains partial.")
    if program == "tots":
        gaps.append("The KB supports movement-led tots programming, but exact game ordering is still editorial.")
    return unique_strings(gaps)


def build_pair_week(
    program: str,
    week_number: int,
    pair_spec: dict,
    variant: dict,
    shared_gap_refs: list[str],
) -> dict:
    cycle = pair_spec["cycle"]
    if program == "adult":
        cycle = adult_cycle_for_week(week_number, cycle if cycle != "special" else "offensive")
    elif cycle == "special":
        cycle = "offensive"

    theme = f"{pair_spec['theme']}: {variant['title']}"
    if program == "adult" and week_number == 23:
        theme = "Lower-Body Awareness: Offensive Entries"
    if program == "adult" and week_number == 24:
        theme = "Lower-Body Awareness: Defensive Clearing"

    teaching_goal = f"{pair_spec['focus_core']} {variant['focus_suffix']}"
    week = {
        "week": week_number,
        "cycle": cycle,
        "theme": theme,
        "focus": pair_spec["focus_core"],
        "teaching_goal": teaching_goal,
        "takedown": pair_spec["takedown"],
        "ground": pair_spec["ground"],
        "submission": pair_spec["submission"],
        "level_1": f"{pair_spec['level_1']} {variant['level_1_suffix']}",
        "level_2": f"{pair_spec['level_2']} {variant['level_2_suffix']}",
        "coach_notes": f"{pair_spec['coach_notes']} {variant['coach_suffix']}",
        "theme_basis": "heuristic",
        "takedown_basis": "heuristic",
        "ground_basis": "heuristic",
        "submission_basis": "heuristic",
        "expert_review_notes": build_pair_review_notes(program, pair_spec["theme"], week_number, variant["review_note"]),
        "kb_gaps": build_week_kb_gaps(program, week_number, shared_gap_refs),
    }
    if program == "adult":
        adult_note = "Allow more realistic grip fighting, pressure, and posting reactions once the core mechanics are stable."
        if week_number >= 23:
            adult_note = "Keep the lower-body material rules-aware, safety-aware, and explicitly provisional pending expert review."
        week["adult_specific_notes"] = adult_note
    return week


def build_pair_program_weeks(program: str, pair_specs: tuple[dict, ...], shared_gap_refs: list[str]) -> list[dict]:
    weeks: list[dict] = []
    for pair_index, pair_spec in enumerate(pair_specs):
        variants = OFFENSIVE_VARIANTS if pair_spec["cycle"] in {"offensive", "special"} else DEFENSIVE_VARIANTS
        first_week_number = pair_index * 2 + 1
        for offset, variant in enumerate(variants):
            weeks.append(build_pair_week(program, first_week_number + offset, pair_spec, variant, shared_gap_refs))
    return weeks


def build_youth_weeks(shared_gap_refs: list[str]) -> list[dict]:
    return build_pair_program_weeks("youth", YOUTH_PAIR_SPECS, shared_gap_refs)


def build_adult_weeks(shared_gap_refs: list[str]) -> list[dict]:
    return build_pair_program_weeks("adult", ADULT_PAIR_SPECS, shared_gap_refs)


def build_tots_weeks(shared_gap_refs: list[str]) -> list[dict]:
    weeks: list[dict] = []
    for week_number, spec in enumerate(TOTS_WEEK_SPECS, start=1):
        week = {
            "week": week_number,
            "cycle": spec["cycle"],
            "theme": spec["theme"],
            "movement_theme": spec["movement_theme"],
            "game": spec["game"],
            "coordination_focus": spec["coordination_focus"],
            "bjj_exposure": spec["bjj_exposure"],
            "coach_notes": spec["coach_notes"],
            "theme_basis": "heuristic",
            "expert_review_notes": build_pair_review_notes("tots", spec["theme"], week_number, "Confirm the game-to-movement pairing works for the local class flow."),
            "kb_gaps": build_week_kb_gaps("tots", week_number, shared_gap_refs),
        }
        weeks.append(week)
    return weeks


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
    confidence = metadata.get("confidence", "0.60")

    source_lines = source_kb_pages or []
    warnings = metadata.get("warnings") or ["Week ordering is heuristic because the KB does not contain a source-authored calendar."]
    generation_notes = metadata.get("generation_notes") or ["Deterministic two-stage curriculum generator artifact."]
    kb_gap_refs = metadata.get("kb_gap_refs") or []

    lines = [
        "---",
        f"id: {page_id}",
        "type: generated-curriculum-candidate",
        f'title: "{title}"',
        "status: provisional",
        "synthesis_mode: heuristic",
        "expert_review_required: true",
        "source_kb_pages:",
    ]
    lines.extend(f"  - {page}" for page in source_lines)
    lines.append("generation_notes:")
    lines.extend(f"  - {note}" for note in generation_notes)
    lines.append("warnings:")
    lines.extend(f"  - {warning}" for warning in warnings)
    if kb_gap_refs:
        lines.append("kb_gap_refs:")
        lines.extend(f"  - {gap_ref}" for gap_ref in kb_gap_refs)
    lines.extend(
        [
            f"confidence: {confidence}",
            "---",
            f"# {title}",
            "",
            f"Provisional {program} week map synthesized heuristically from KB frameworks. Expert review is required before treating this sequence as authoritative.",
            "",
            "```json",
            json.dumps({"weeks": weeks}, indent=2),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def program_required_kb_pages(program: str) -> tuple[str, ...]:
    return tuple(PROGRAM_CONFIG[program]["required_kb_pages"])


def validate_program_framework_inputs(repo_root: Path, job_spec: dict, program: str) -> tuple[list[str], dict, dict[str, tuple[dict, str]]]:
    configured_pages = set(configured_kb_pages(job_spec))
    required_pages = program_required_kb_pages(program)
    missing_inputs = [page for page in required_pages if page not in configured_pages]
    if missing_inputs:
        missing_list = ", ".join(missing_inputs)
        raise ValueError(f"missing required framework input for {program}: {missing_list}")

    primary_page = PROGRAM_CONFIG[program]["primary_framework_page"]
    primary_metadata: dict | None = None
    framework_pages: dict[str, tuple[dict, str]] = {}
    for relative_path in required_pages:
        metadata, body = read_kb_page(repo_root, relative_path)
        framework_pages[relative_path] = (metadata, body)
        if relative_path == primary_page:
            primary_metadata = metadata

    if primary_metadata is None:
        raise ValueError(f"missing required framework page: {primary_page}")
    return list(required_pages), primary_metadata, framework_pages


def synthesize_program_weeks(program: str, shared_gap_refs: list[str]) -> list[dict]:
    if program == "youth":
        return build_youth_weeks(shared_gap_refs)
    if program == "adult":
        return build_adult_weeks(shared_gap_refs)
    if program == "tots":
        return build_tots_weeks(shared_gap_refs)
    raise ValueError(f"unknown program: {program}")


def synthesize_program_week_map(repo_root: Path, job_spec: dict, program: str) -> str:
    source_kb_pages, _primary_metadata, framework_pages = validate_program_framework_inputs(repo_root, job_spec, program)
    shared_gap_refs = framework_gap_refs(framework_pages, limit=4)
    return render_generated_week_map(
        program,
        source_kb_pages,
        synthesize_program_weeks(program, shared_gap_refs),
        metadata={
            "confidence": heuristic_confidence(framework_pages),
            "generation_notes": [
                "Deterministic heuristic synthesis from configured framework KB pages.",
                "Week ordering and pairings are editorial-normalization pending expert review.",
            ],
            "id": f"generated-{program}-week-map",
            "title": PROGRAM_CONFIG[program]["default_title"],
            "warnings": unique_strings(
                [
                    "The KB frameworks define constraints and families, but they do not author a final week-by-week calendar.",
                    *shared_gap_refs[:2],
                ]
            ),
            "kb_gap_refs": shared_gap_refs,
        },
    )


def write_generated_week_maps(repo_root: Path, job_spec: dict, job_context: dict) -> list[str]:
    output_paths: list[str] = []
    week_maps_root = reset_output_dir(repo_root / "generated" / job_context["job_name"] / "week-maps")
    for program in PROGRAM_CONFIG:
        page_path = week_maps_root / PROGRAM_CONFIG[program]["generated_filename"]
        page_text = synthesize_program_week_map(repo_root, job_spec, program)
        write_text(page_path, page_text, overwrite=True)
        output_paths.append(page_path.relative_to(repo_root).as_posix())
    return output_paths


def validate_generated_week_map_metadata(page_path: Path, metadata: dict) -> None:
    required_list_fields = ("source_kb_pages", "generation_notes", "warnings")
    missing = [field for field in required_list_fields if not metadata.get(field)]
    if missing:
        raise ValueError(f"generated week map metadata missing {', '.join(missing)} in {page_path}")
    if metadata.get("synthesis_mode") != "heuristic":
        raise ValueError(f"generated week map must declare synthesis_mode: heuristic in {page_path}")
    if metadata.get("expert_review_required") is not True:
        raise ValueError(f"generated week map must declare expert_review_required: true in {page_path}")
    if metadata.get("confidence") in {None, ""}:
        raise ValueError(f"generated week map metadata missing confidence in {page_path}")


def validate_generated_week_entry(program: str, week: dict, page_path: Path) -> None:
    common_required = ("week", "cycle", "theme", "coach_notes", "theme_basis", "expert_review_notes", "kb_gaps")
    if program == "tots":
        required = common_required + ("movement_theme", "game", "coordination_focus", "bjj_exposure")
    else:
        required = common_required + (
            "focus",
            "teaching_goal",
            "takedown",
            "ground",
            "submission",
            "level_1",
            "level_2",
            "takedown_basis",
            "ground_basis",
            "submission_basis",
        )
    missing = [field for field in required if field not in week or week[field] in (None, "")]
    if missing:
        raise ValueError(f"generated week entry missing {', '.join(missing)} in {page_path}")


def load_generated_program_data(repo_root: Path, job_name: str, program: str) -> tuple[dict, list[dict]]:
    page_path = generated_week_map_path(repo_root, job_name, program)
    if not page_path.exists():
        raise FileNotFoundError(f"missing generated week map: {page_path.relative_to(repo_root).as_posix()}")
    _, metadata, weeks = load_week_map_page(page_path)
    validate_generated_week_map_metadata(page_path, metadata)
    for week in weeks:
        validate_generated_week_entry(program, week, page_path)
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


def render_provisional_marker(metadata: dict) -> list[str]:
    status = REVIEW_STATUS if metadata.get("synthesis_mode") == "heuristic" else str(metadata.get("status", "generated"))
    review_required = "yes" if metadata.get("expert_review_required") else "no"
    return [
        "## Curriculum Status",
        f"- Curriculum Status: {status}",
        f"- Expert Review Required: {review_required}",
    ]


def render_program_syllabus(program: str, weeks: list[dict]) -> str:
    title = PROGRAM_CONFIG[program]["program_title"]
    lines = [
        f"# {title} Program Syllabus",
        "",
        f"This provisional syllabus maps the {title.lower()} weekly sequence to its cycle, theme, description, and main goal.",
        "",
        "| Week | Cycle | Theme | Description | Main Goal |",
        "| --- | --- | --- | --- | --- |",
    ]

    for week in weeks:
        if program == "tots":
            description = week.get("movement_theme", "Not specified")
            main_goal = week.get("coach_notes", "Not specified")
        else:
            description = week.get("ground", "Not specified")
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
        *render_provisional_marker(metadata),
        "",
        "## Snapshot",
        f"- Theme: {week['theme']}",
        f"- Cycle: {week.get('cycle', 'unspecified')}",
        f"- Focus: {week.get('focus', 'Not specified')}",
        f"- Teaching Goal: {week.get('teaching_goal', 'Not specified')}",
        f"- Class Length: {PROGRAM_CONFIG[program]['class_length']}",
        f"- Source Basis: {source_basis(metadata)}",
        "",
        "## Takedown Theme",
        week.get("takedown", "Not specified"),
        "",
        "## Ground Theme",
        week.get("ground", "Not specified"),
        "",
        "## Submission Connection",
        week.get("submission", "Not specified"),
        "",
        "## Coach Notes",
        week.get("coach_notes", "No coach notes provided."),
        "",
        "## Level 1",
        f"- {week.get('level_1', 'Not specified')}",
        "",
        "## Level 2",
        f"- {week.get('level_2', 'Not specified')}",
    ]
    if program == "adult":
        lines.extend(
            [
                "",
                "## Adult-Specific Notes",
                week.get("adult_specific_notes", "Use the youth framework and add adult-specific context where needed."),
            ]
        )

    return "\n".join(lines) + "\n"


def render_tots_curriculum(metadata: dict, week: dict) -> str:
    lines = [
        f"# Tots Week {week['week']:02d} Curriculum",
        "",
        *render_metadata_block("tots", week),
        "",
        *render_provisional_marker(metadata),
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


def render_quick_outline(program: str, metadata: dict, week: dict) -> str:
    lines = [
        f"# {PROGRAM_CONFIG[program]['program_title']} Week {week['week']:02d} Quick Outline",
        "",
        *render_metadata_block(program, week),
        "",
        *render_provisional_marker(metadata),
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
        lines.extend(
            [
                f"- Takedown: {week.get('takedown', 'Not specified')}",
                f"- Ground: {week.get('ground', 'Not specified')}",
                f"- Submission: {week.get('submission', 'Not specified')}",
            ]
        )
    return "\n".join(lines) + "\n"


def render_coach_guide(program: str, metadata: dict, week: dict) -> str:
    lines = [
        f"# {PROGRAM_CONFIG[program]['program_title']} Week {week['week']:02d} Coach Guide",
        "",
        *render_metadata_block(program, week),
        "",
        *render_provisional_marker(metadata),
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
                "## Activity Map",
                f"- Movement Theme: {week.get('movement_theme', 'Not specified')}",
                f"- Game: {week.get('game', 'Not specified')}",
                f"- Intro Grappling Exposure: {week.get('bjj_exposure', 'Not specified')}",
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
                "## Technical Map",
                f"- Takedown Theme: {week.get('takedown', 'Not specified')}",
                f"- Ground Theme: {week.get('ground', 'Not specified')}",
                f"- Submission Connection: {week.get('submission', 'Not specified')}",
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


def render_fully_scripted_session(program: str, metadata: dict, week: dict) -> str:
    title = PROGRAM_CONFIG[program]["program_title"]
    lines = [
        f"# {title} Week {week['week']:02d} Fully Scripted Session",
        "",
        *render_metadata_block(program, week),
        "",
        *render_provisional_marker(metadata),
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
        lines.extend(
            [
                "",
                "## Takedown Block",
                f"Show the standing connection first: {prose(week.get('takedown', 'Not specified'))}.",
                "",
                "## Ground Block",
                f"Land directly into the ground theme: {prose(week.get('ground', 'Not specified'))}.",
                "",
                "## Submission Block",
                f"Only add the finishing layer that naturally grows from the ground exchange: {prose(week.get('submission', 'Not specified'))}.",
                "",
                "## Leveling Block",
                f"Teach Level 1 as the base pattern: {prose(week.get('level_1', 'Not specified'))}.",
                f"Layer Level 2 only after the room is stable: {prose(week.get('level_2', 'Not specified'))}.",
                f"Repeat the coach emphasis: {prose(week.get('coach_notes', 'Not specified'))}.",
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
        return render_quick_outline(program, metadata, week)
    if output_type == "coach-guide":
        return render_coach_guide(program, metadata, week)
    if output_type == "fully-scripted-session":
        return render_fully_scripted_session(program, metadata, week)
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
