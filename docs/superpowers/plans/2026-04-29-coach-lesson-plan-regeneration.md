# Coach Lesson Plan Regeneration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Regenerate `kin-bjj-coach-lesson-plans` from the denser active KB, archive the current generated output tree under `generated/kin-bjj-coach-lesson-plans-old/`, and replace repeated weekly missing-info files with one consolidated `missing-info.md` per program.

**Architecture:** Keep the existing `coach_lesson_plans` job and deterministic heuristic sequencing, but widen the generator’s KB input set and add a deterministic KB-detail extraction layer that enriches lesson sections with reusable coaching detail from the denser KB page bodies. Preserve weekly `kb-grounding` files, collapse repeated missing-info into per-program meta files, and archive the prior generated output tree before writing the new one.

**Tech Stack:** Python 3, repo-local `llm-knowledge-base` scripts, markdown generation, pytest

---

## File Structure

- Modify: `repo_generators/coach_lesson_plans.py`
  - Add archive behavior for the generated output tree.
  - Expand KB input handling and deterministic KB-detail extraction.
  - Make lesson rendering less terse while keeping list-heavy coach format.
  - Replace repeated weekly missing-info files with one per-program aggregate file.
- Modify: `jobs/kin-bjj-coach-lesson-plans/job.yaml`
  - Expand `kb_pages` to include the denser KB framework and program pages the generator should mine.
- Modify: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`
  - Cover archive behavior, denser lesson output, and consolidated program-level `missing-info.md`.
- Modify: `tests/skills/llm_knowledge_base/test_run_generation.py`
  - Keep runner-level coverage aligned with the new coach-job output contract if any path assertions need updating.
- Regenerate: `generated/kin-bjj-coach-lesson-plans/**`
  - Fresh coach-facing output tree.
- Archive: `generated/kin-bjj-coach-lesson-plans-old/**`
  - Previous output tree moved here deterministically.

### Task 1: Lock In the New Output Contract With Tests

**Files:**
- Modify: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`

- [ ] **Step 1: Extend the seeded KB fixture with dense page bodies the generator can mine**

Add richer test fixtures so the generator can pull coach-useful detail from KB bodies instead of only from the example lesson pages.

```python
write_page(
    repo / "kb" / "position" / "guard-framework.md",
    """---
id: guard-framework
type: position
title: "Guard Framework"
status: active
confidence: 0.86
claim_label: editorial-normalization
source_refs:
  - source-compendium#chunk-guard-001
related_pages: []
domain_tags: [guard, bottom-game]
keywords: [guard framework, guard retention, bottom position]
summary: Guard is treated as a bottom-position system built on retention, recovery, sweeping threats, and submission connections.
---
# Guard Framework

## Definition

Guard is the bottom-position framework for controlling distance, recovering structure, and launching reversals or attacks.

## Detailed Notes

- Guard work should begin with posture and connection before students chase speed.
- Recovery, retention, and immediate re-guarding are stronger teaching priorities than low-percentage scramble reactions.

## Operational Implications

- Coaches should cue structure before attack volume.
- Early weeks should reward calm guard recovery and connected follow-up.
""",
)
```

- [ ] **Step 2: Replace the weekly missing-info assertions with program-level assertions**

Update the output-shape test so it expects:

```python
assert (repo / "generated" / "coach-job" / "meta" / "adult" / "week-01-kb-grounding.md").exists()
assert (repo / "generated" / "coach-job" / "meta" / "adult" / "missing-info.md").exists()
assert not (repo / "generated" / "coach-job" / "meta" / "adult" / "week-01-missing-info.md").exists()
```

- [ ] **Step 3: Add an archive-behavior test**

Write a failing test that seeds an existing output tree, seeds an existing `generated/coach-job-old/` tree, runs generation, and asserts the old folder was deterministically replaced.

```python
def test_generate_coach_lesson_plans_archives_existing_output_tree(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_example_kb(repo)
    write_job(repo)

    current_root = repo / "generated" / "coach-job"
    archived_root = repo / "generated" / "coach-job-old"
    write_page(current_root / "lesson" / "adult" / "week-01-lesson-plan.md", "current output")
    write_page(archived_root / "stale.md", "stale archive")

    subprocess.run([sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "coach-job"], check=True)

    assert (archived_root / "lesson" / "adult" / "week-01-lesson-plan.md").exists()
    assert not (archived_root / "stale.md").exists()
    assert (current_root / "lesson" / "adult" / "week-01-lesson-plan.md").exists()
```

- [ ] **Step 4: Add a denser-lesson-content test**

Require the adult lesson file to contain pulled coaching detail, not just the old skeletal lines.

```python
lesson_text = (repo / "generated" / "coach-job" / "lesson" / "adult" / "week-01-lesson-plan.md").read_text(encoding="utf-8")

assert "frames before escape attempts" in lesson_text or "structure before attack volume" in lesson_text
assert "Keep the room moving with short explanation windows and clear reset points." in lesson_text
assert "source_refs" not in lesson_text
```

- [ ] **Step 5: Run the focused coach generator test file and verify the new assertions fail first**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py -q
```

Expected: failing assertions for missing archive behavior, missing consolidated `missing-info.md`, and missing denser lesson content.

- [ ] **Step 6: Commit the failing-test changes**

```bash
git add tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py
git commit -m "test: cover coach lesson plan archive and dense output contract"
```

### Task 2: Implement Output Archiving and Consolidated Missing-Info Files

**Files:**
- Modify: `repo_generators/coach_lesson_plans.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`

- [ ] **Step 1: Add deterministic archive handling for the generated output tree**

Replace the current unconditional reset behavior with an archive helper.

```python
def archive_and_reset_output_dir(path: Path) -> Path:
    archived_path = path.with_name(f"{path.name}-old")
    if archived_path.exists():
        shutil.rmtree(archived_path)
    if path.exists():
        path.rename(archived_path)
    return ensure_dir(path)
```

Update `generate()` to use:

```python
output_root = archive_and_reset_output_dir(repo_root / "generated" / job_context["job_name"])
```

- [ ] **Step 2: Add program-level missing-info rendering**

Replace `render_missing_info(week)` with a program-level aggregator:

```python
def render_program_missing_info(program: str, weeks: list[dict]) -> str:
    shared_gaps: list[str] = []
    seen_shared: set[str] = set()
    week_sections: list[str] = []

    for week in weeks:
        for gap in week["kb_gaps"]:
            if gap not in seen_shared:
                seen_shared.add(gap)
                shared_gaps.append(gap)

        week_sections.extend(
            [
                f"## Week {week['week']:02d}",
                f"- Theme: {week['theme']}",
                *week["missing_info_prompts"],
                "",
            ]
        )

    return "\n".join(
        [
            f"# {PROGRAM_RULES[program]['title']} Missing Information",
            "",
            "## Shared Gaps",
            *[f"- {gap}" for gap in shared_gaps],
            "",
            "## Week-Specific Decisions",
            *week_sections,
        ]
    ).rstrip() + "\n"
```

- [ ] **Step 3: Move week-specific prompts into synthesized week data**

Store fill-in prompts once during synthesis so program aggregation is deterministic.

```python
"missing_info_prompts": [
    "- Preferred class-length adjustment: ____________________",
    "- Specific emphasis or theme rename for this week: ____________________",
]
```

Then append program-specific prompts:

```python
if program == "adult":
    prompts.append("- Allowed leg-lock depth or restrictions for this group: ____________________")
elif program == "youth":
    prompts.append("- Preferred self-defence scenario framing for this group: ____________________")
else:
    prompts.append("- Preferred substitute game if attention is low: ____________________")
```

- [ ] **Step 4: Update file writes in `generate()`**

Keep weekly grounding files, remove weekly missing-info writes, and write one aggregated file per program.

```python
program_missing_info_path = meta_root / program / "missing-info.md"
write_text(program_missing_info_path, render_program_missing_info(program, weeks), overwrite=True)
outputs.append(program_missing_info_path.relative_to(repo_root).as_posix())

for week in weeks:
    grounding_path = meta_root / program / f"week-{week['week']:02d}-kb-grounding.md"
    write_text(grounding_path, render_kb_grounding(week, kb_pages), overwrite=True)
```

- [ ] **Step 5: Run the focused coach generator tests and verify these output-shape failures are resolved**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py -q
```

Expected: archive and `missing-info.md` output-shape assertions pass, while dense-content assertions may still fail.

- [ ] **Step 6: Commit the archive and meta-structure implementation**

```bash
git add repo_generators/coach_lesson_plans.py tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py
git commit -m "feat: archive coach lesson plan outputs and consolidate missing info"
```

### Task 3: Mine the Denser KB and Enrich Lesson Rendering

**Files:**
- Modify: `repo_generators/coach_lesson_plans.py`
- Modify: `jobs/kin-bjj-coach-lesson-plans/job.yaml`
- Test: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`

- [ ] **Step 1: Expand the coach job’s KB input set**

Add the denser KB pages the generator should use directly.

```yaml
inputs:
  kb_pages:
    - kb/sources/high-level-overview.md
    - kb/sources/kin-bjj-compendium.md
    - kb/sources/kin-bjj-kids-lesson-plan-structure.md
    - kb/lessons/double-leg-side-control-americana-example-lesson.md
    - kb/lessons/tots-week-1-mat-rules-base-ready-stance-example.md
    - kb/concepts/four-layers-of-bjj-skill-development.md
    - kb/concepts/escape-framework.md
    - kb/concepts/movement-and-warmup-framework.md
    - kb/concepts/submission-framework.md
    - kb/position/guard-framework.md
    - kb/position/side-control-system.md
    - kb/class-types/class-structure-principles.md
    - kb/class-types/competition-training-session-framework.md
    - kb/procedures/technical-lesson-delivery-model.md
    - kb/procedures/example-lesson-warmup-option-pattern.md
    - kb/procedures/example-situational-start-pattern.md
    - kb/programs/kids-youth-development-program.md
```

- [ ] **Step 2: Add a deterministic KB-snippet extraction layer**

Introduce small helpers that read page bodies by section header and return reusable bullet text.

```python
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
```

Build a deterministic detail bundle:

```python
def build_kb_detail_bundle(kb_pages: dict[str, dict]) -> dict[str, list[str]]:
    return {
        "guard_operational": extract_section_bullets(kb_pages["guard-framework"]["body"], "Operational Implications"),
        "escape_notes": extract_section_bullets(kb_pages["escape-framework"]["body"], "Detailed Notes"),
        "warmup_notes": extract_section_bullets(kb_pages["movement-and-warmup-framework"]["body"], "Operational Implications"),
        "submission_notes": extract_section_bullets(kb_pages["submission-framework"]["body"], "Constraints or Safety Notes"),
        "youth_program_notes": extract_section_bullets(kb_pages["kids-youth-development-program"]["body"], "Operational Implications"),
    }
```

- [ ] **Step 3: Thread the KB detail bundle into week synthesis**

Update synthesis so each week carries deterministic enrichment fields.

```python
"opening_emphasis": detail_bundle["escape_notes"][:2],
"warmup_emphasis": detail_bundle["warmup_notes"][:2],
"ground_emphasis": detail_bundle["guard_operational"][:2],
"submission_safety": detail_bundle["submission_notes"][:2],
"program_framing": detail_bundle["youth_program_notes"][:2] if program == "youth" else [],
```

- [ ] **Step 4: Expand adult/youth lesson rendering with richer list-heavy content**

Keep the coach-facing structure, but turn the sparse one-liners into denser bullet groups.

```python
"## Opening Script",
f"- Theme setup: {week['theme']}.",
f"- Main goal: {week['teaching_goal']}",
*[f"- Emphasis: {item}" for item in week["opening_emphasis"]],
"",
"## Warm-Up Options",
"- **Movement Based**",
f"  - {week['warmup_movement']}",
*[f"  - Coaching Emphasis: {item}" for item in week["warmup_emphasis"]],
```

For ground and submission blocks:

```python
f"- **Ground: {ground_label}**",
f"  - Secure: {week['ground']}",
*[f"  - Coaching Emphasis: {item}" for item in week["ground_emphasis"]],
```

And for offensive weeks:

```python
f"- **Submission: {submission_label}**",
f"  - Cue: {week['submission']}",
*[f"  - Safety: {item}" for item in week["submission_safety"]],
```

- [ ] **Step 5: Expand tots rendering from the denser KB**

Use warm-up and behavior framing from the KB for the tots sections:

```python
"### Coach Notes",
f"- {week['coach_focus']}",
*[f"- Coaching Emphasis: {item}" for item in week["warmup_emphasis"]],
"- Keep transitions short and celebrate good listening quickly.",
```

- [ ] **Step 6: Update KB-grounding rendering so inferred vs KB-grounded notes reference the richer KB inputs**

Keep the same sections, but make the direct support line items concrete:

```python
direct_support = [
    "- Preserved lesson-format examples provide the markdown shape for the lesson file.",
    "- Guard, escape, submission, class-structure, and lesson-delivery KB pages provide coaching detail for openings, warm-ups, technical emphasis, and safety notes.",
]
```

- [ ] **Step 7: Run the focused coach generator tests and make them pass**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py -q
```

Expected: PASS

- [ ] **Step 8: Commit the KB-informed lesson rendering changes**

```bash
git add repo_generators/coach_lesson_plans.py jobs/kin-bjj-coach-lesson-plans/job.yaml tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py
git commit -m "feat: enrich coach lesson plans from detailed kb pages"
```

### Task 4: Runner Verification and Full Regeneration

**Files:**
- Modify: `tests/skills/llm_knowledge_base/test_run_generation.py` if needed
- Regenerate: `generated/kin-bjj-coach-lesson-plans/**`
- Archive: `generated/kin-bjj-coach-lesson-plans-old/**`

- [ ] **Step 1: Update runner-level assertions only if the changed output contract requires it**

If `test_run_generation.py` asserts on the old per-week missing-info shape, change it to the new aggregate path:

```python
assert (repo / "generated" / "coach-job" / "meta" / "adult" / "missing-info.md").exists()
assert not (repo / "generated" / "coach-job" / "meta" / "adult" / "week-01-missing-info.md").exists()
```

- [ ] **Step 2: Run the runner and coach generator test suite**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py tests/skills/llm_knowledge_base/test_run_generation.py -q
```

Expected: PASS

- [ ] **Step 3: Run bytecode verification for the generator**

Run:

```bash
python3 -m py_compile repo_generators/coach_lesson_plans.py
```

Expected: no output

- [ ] **Step 4: Regenerate the real job output**

Run:

```bash
python3 skills/llm-knowledge-base/scripts/run_generation.py . --job-name kin-bjj-coach-lesson-plans
```

Expected:

- `generated/kin-bjj-coach-lesson-plans-old/` contains the prior output snapshot
- `generated/kin-bjj-coach-lesson-plans/lesson/` contains fresh syllabus and lesson files
- `generated/kin-bjj-coach-lesson-plans/meta/<program>/missing-info.md` exists once per program
- weekly `week-XX-kb-grounding.md` files exist

- [ ] **Step 5: Spot-check the regenerated output for density**

Inspect:

```bash
sed -n '1,220p' generated/kin-bjj-coach-lesson-plans/lesson/adult/week-01-lesson-plan.md
sed -n '1,220p' generated/kin-bjj-coach-lesson-plans/meta/adult/missing-info.md
sed -n '1,220p' generated/kin-bjj-coach-lesson-plans-old/lesson/adult/week-01-lesson-plan.md
```

Expected:

- the new lesson file is visibly denser and more specific than the archived one
- the new `missing-info.md` removes repeated weekly boilerplate

- [ ] **Step 6: Commit the regenerated output and any runner-test updates**

```bash
git add tests/skills/llm_knowledge_base/test_run_generation.py generated/kin-bjj-coach-lesson-plans generated/kin-bjj-coach-lesson-plans-old
git commit -m "chore: regenerate coach lesson plans from detailed kb"
```

## Self-Review

- Spec coverage:
  - archive old generated output: Task 2 and Task 4
  - consolidated per-program `missing-info.md`: Task 2 and Task 4
  - less terse lesson content from denser KB: Task 1 and Task 3
  - preserve weekly grounding files: Task 2 and Task 4
  - deterministic KB selection and synthesis: Task 3
- Placeholder scan:
  - no `TODO`, `TBD`, or deferred implementation markers remain
- Type consistency:
  - helper names, output paths, and prompt fields are defined before later tasks refer to them
