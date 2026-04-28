# KIN Coach Offensive Submission Block Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update adult and youth coach lesson rendering so offensive-cycle weeks include a standalone submission block while situational options remain present for both offensive and defensive cycles.

**Architecture:** Keep the change local to `repo_generators/coach_lesson_plans.py` and its tests. Extend the coach-plan test fixture to assert offensive vs defensive formatting, then update the adult/youth lesson renderer to branch by `cycle` and move submission text out of the ground block for offensive weeks only.

**Tech Stack:** Python 3, pytest, repo-local generator runner

---

### Task 1: Add failing tests for offensive vs defensive lesson formatting

**Files:**
- Modify: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`

- [ ] **Step 1: Add an offensive-cycle assertion test**

```python
def test_generate_coach_lesson_plans_offensive_cycles_render_submission_block(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_example_kb(repo)
    write_job(repo)

    subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "coach-job"],
        capture_output=True,
        text=True,
        check=True,
    )

    lesson_text = (repo / "generated" / "coach-job" / "lesson" / "adult" / "week-01-lesson-plan.md").read_text(
        encoding="utf-8"
    )

    assert "- **Submission:" in lesson_text
    assert "- **Situational Options**" in lesson_text
```

- [ ] **Step 2: Add a defensive-cycle assertion test**

```python
def test_generate_coach_lesson_plans_defensive_cycles_keep_situational_without_submission_block(tmp_path):
    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)
    seed_example_kb(repo)
    write_job(repo)

    subprocess.run(
        [sys.executable, str(RUN_SCRIPT), str(repo), "--job-name", "coach-job"],
        capture_output=True,
        text=True,
        check=True,
    )

    lesson_text = (repo / "generated" / "coach-job" / "lesson" / "adult" / "week-03-lesson-plan.md").read_text(
        encoding="utf-8"
    )

    assert "- **Submission:" not in lesson_text
    assert "- **Situational Options**" in lesson_text
```

- [ ] **Step 3: Tighten the existing format test so the old inline wording cannot survive**

```python
def test_generate_coach_lesson_plans_keep_provenance_out_of_lesson_files(tmp_path):
    ...
    assert "Submission / Win Condition" not in lesson_text
```

- [ ] **Step 4: Run the focused test file to confirm the renderer currently fails**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py -q`

Expected: FAIL because offensive weeks do not yet render a standalone submission block and still use the older inline wording.

- [ ] **Step 5: Commit the red-test checkpoint**

```bash
git add tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py
git commit -m "test: cover offensive submission block formatting"
```

### Task 2: Update adult/youth lesson rendering by cycle

**Files:**
- Modify: `repo_generators/coach_lesson_plans.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`

- [ ] **Step 1: Add a small helper that renders the middle lesson blocks by cycle**

```python
def render_adult_or_youth_lesson_blocks(week: dict) -> list[str]:
    blocks = [
        "- **Takedown**",
        f"  - Coaching Tip: {week['coach_focus']}",
        f"  - Level 1: {week['takedown']}",
        "  - Level 2: Add timing, angle change, or chain-attack follow-up without increasing chaos.",
        f"  - Outcome: Finish to a clean top position that leads into {week['ground'].split('.', 1)[0].lower()}",
        f"- **Ground: {week['ground'].split('.', 1)[0]}**",
        f"  - Secure: {week['ground']}",
        "  - Level 2: Add a simple transition or pressure-retention task before the finish.",
    ]
    if week["cycle"] == "offensive":
        blocks.extend(
            [
                f"- **Submission: {week['submission'].split('.', 1)[0]}**",
                f"  - Cue: {week['submission']}",
            ]
        )
    blocks.extend(
        [
            "- **Situational Options**",
            f"  - {week['situational']}",
            "  - Run short rounds with a fast reset after the first clean win condition or escape.",
        ]
    )
    return blocks
```

- [ ] **Step 2: Use the helper inside `render_adult_or_youth_lesson()`**

```python
def render_adult_or_youth_lesson(week: dict) -> str:
    title = PROGRAM_RULES[week["program"]]["title"]
    return "\n".join(
        [
            f"# Week {week['week']} ({week['cycle'].title()} Cycle)",
            ...
            f"## Lesson: {week['theme']}",
            *render_adult_or_youth_lesson_blocks(week),
            "",
            "## Coach Notes",
            ...
        ]
    )
```

- [ ] **Step 3: Remove the old inline `Submission / Win Condition` wording from the ground block**

```python
# delete this older line from render_adult_or_youth_lesson():
f"  - Submission / Win Condition: {week['submission']}",
```

- [ ] **Step 4: Run the focused coach lesson plan tests**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py -q`

Expected: PASS

- [ ] **Step 5: Commit the renderer change**

```bash
git add repo_generators/coach_lesson_plans.py tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py
git commit -m "feat: add offensive submission block to coach lessons"
```

### Task 3: Verify generated outputs and regenerate the real job

**Files:**
- Modify: `generated/kin-bjj-coach-lesson-plans/lesson/adult/*.md`
- Modify: `generated/kin-bjj-coach-lesson-plans/lesson/youth/*.md`
- Modify: `generated/kin-bjj-coach-lesson-plans/_meta/run.json`

- [ ] **Step 1: Run the broader verification set**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py tests/skills/llm_knowledge_base/test_run_generation.py tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`

Expected: PASS

- [ ] **Step 2: Run bytecode verification**

Run: `python3 -m py_compile repo_generators/coach_lesson_plans.py`

Expected: no output

- [ ] **Step 3: Regenerate the real coach lesson plan job**

Run: `python3 skills/llm-knowledge-base/scripts/run_generation.py . --job-name kin-bjj-coach-lesson-plans`

Expected: updated lesson files under:
- `generated/kin-bjj-coach-lesson-plans/lesson/adult/`
- `generated/kin-bjj-coach-lesson-plans/lesson/youth/`

- [ ] **Step 4: Manually inspect one offensive and one defensive lesson**

Checklist:
- `generated/kin-bjj-coach-lesson-plans/lesson/adult/week-01-lesson-plan.md` contains `- **Submission:`
- `generated/kin-bjj-coach-lesson-plans/lesson/adult/week-03-lesson-plan.md` does not contain `- **Submission:`
- both files contain `- **Situational Options**`
- tots files are unchanged in structure

- [ ] **Step 5: Commit regenerated outputs if they changed**

```bash
git add repo_generators/coach_lesson_plans.py tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py generated/kin-bjj-coach-lesson-plans
git commit -m "chore: regenerate coach lesson plans with submission block"
```
