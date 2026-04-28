# KIN Coach Syllabus Table Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Change all generated coach syllabus files to a four-column markdown table format with `Week`, `Cycle`, `Theme`, and `Main Goal`.

**Architecture:** Keep the change local to `repo_generators/coach_lesson_plans.py` and its tests. Replace the current bullet-based syllabus renderer with a compact markdown-table renderer, extend test coverage for adult/youth/tots syllabus format, and regenerate the real `kin-bjj-coach-lesson-plans` outputs.

**Tech Stack:** Python 3, pytest, repo-local generation runner

---

### Task 1: Add failing tests for syllabus table output

**Files:**
- Modify: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`

- [ ] **Step 1: Add a table-format assertion for the adult syllabus**

```python
def test_generate_coach_lesson_plans_adult_syllabus_uses_table_format(tmp_path):
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

    syllabus_text = (repo / "generated" / "coach-job" / "lesson" / "adult-syllabus.md").read_text(encoding="utf-8")

    assert "| Week | Cycle | Theme | Main Goal |" in syllabus_text
    assert "| 01 | offensive |" in syllabus_text
    assert "- Program: Adult" not in syllabus_text
    assert "## Coach Note" not in syllabus_text
```

- [ ] **Step 2: Add a shared-format assertion for youth and tots syllabi**

```python
def test_generate_coach_lesson_plans_youth_and_tots_syllabi_use_same_table_format(tmp_path):
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

    youth_text = (repo / "generated" / "coach-job" / "lesson" / "youth-syllabus.md").read_text(encoding="utf-8")
    tots_text = (repo / "generated" / "coach-job" / "lesson" / "tots-syllabus.md").read_text(encoding="utf-8")

    assert "| Week | Cycle | Theme | Main Goal |" in youth_text
    assert "| Week | Cycle | Theme | Main Goal |" in tots_text
    assert "| 01 | offensive |" in youth_text
    assert "| 01 | foundation |" in tots_text
```

- [ ] **Step 3: Run the focused coach lesson plan tests to confirm current failure**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py -q`

Expected: FAIL because the syllabus renderer still emits bullet lists and coach-note footers instead of the table.

- [ ] **Step 4: Commit the red-test checkpoint**

```bash
git add tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py
git commit -m "test: cover syllabus table formatting"
```

### Task 2: Replace the syllabus renderer with a markdown table

**Files:**
- Modify: `repo_generators/coach_lesson_plans.py`
- Test: `tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py`

- [ ] **Step 1: Rewrite `render_syllabus()` to emit the short intro plus a 4-column table**

```python
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
        lines.append(
            f"| {week['week']:02d} | {week['cycle']} | {week['theme']} | {week['teaching_goal']} |"
        )
    lines.append("")
    return "\n".join(lines)
```

- [ ] **Step 2: Remove the old bullet summary and coach-note footer logic**

```python
# delete the older lines:
f"- Program: {title}"
f"- Total Weeks: {len(weeks)}"
f"- Class Length: {PROGRAM_RULES[program]['class_length']}"
"## Weekly Themes"
...
"## Coach Note"
```

- [ ] **Step 3: Run the focused syllabus tests**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py -q`

Expected: PASS

- [ ] **Step 4: Commit the renderer change**

```bash
git add repo_generators/coach_lesson_plans.py tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py
git commit -m "feat: render coach syllabi as tables"
```

### Task 3: Verify and regenerate the real coach outputs

**Files:**
- Modify: `generated/kin-bjj-coach-lesson-plans/lesson/adult-syllabus.md`
- Modify: `generated/kin-bjj-coach-lesson-plans/lesson/youth-syllabus.md`
- Modify: `generated/kin-bjj-coach-lesson-plans/lesson/tots-syllabus.md`
- Modify: `generated/kin-bjj-coach-lesson-plans/_meta/run.json`

- [ ] **Step 1: Run the broader verification set**

Run: `pytest tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py tests/skills/llm_knowledge_base/test_run_generation.py tests/skills/llm_knowledge_base/test_generate_curriculum_outputs.py -q`

Expected: PASS

- [ ] **Step 2: Run bytecode verification**

Run: `python3 -m py_compile repo_generators/coach_lesson_plans.py`

Expected: no output

- [ ] **Step 3: Regenerate the real coach lesson plan job**

Run: `python3 skills/llm-knowledge-base/scripts/run_generation.py . --job-name kin-bjj-coach-lesson-plans`

Expected: updated syllabus files under:
- `generated/kin-bjj-coach-lesson-plans/lesson/adult-syllabus.md`
- `generated/kin-bjj-coach-lesson-plans/lesson/youth-syllabus.md`
- `generated/kin-bjj-coach-lesson-plans/lesson/tots-syllabus.md`

- [ ] **Step 4: Manually inspect the three generated syllabus files**

Checklist:
- all three files have the header `| Week | Cycle | Theme | Main Goal |`
- adult/youth/tots each have zero-padded week rows
- no bullet summary block remains
- no `## Coach Note` footer remains

- [ ] **Step 5: Commit regenerated outputs if they changed**

```bash
git add repo_generators/coach_lesson_plans.py tests/skills/llm_knowledge_base/test_generate_coach_lesson_plan_outputs.py generated/kin-bjj-coach-lesson-plans
git commit -m "chore: regenerate coach syllabi as tables"
```
