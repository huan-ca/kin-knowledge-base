import json
import subprocess
import sys
from pathlib import Path

INIT_SCRIPT = Path("skills/llm-knowledge-base/scripts/init_repo.py").resolve()
REBUILD_SCRIPT = Path("skills/llm-knowledge-base/scripts/rebuild_indexes.py").resolve()


def test_rebuild_indexes_creates_index_gap_report_conflict_report_and_link_map(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"
    assert REBUILD_SCRIPT.exists(), f"missing script: {REBUILD_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    concept_page = repo / "kb" / "concepts" / "closed-guard.md"
    concept_page.parent.mkdir(parents=True, exist_ok=True)
    concept_page.write_text(
        """---
id: closed-guard
type: concept
title: Closed Guard
status: active
confidence: 0.9
source_refs: [source-compendium#chunk-001, source-compendium#chunk-009]
related_pages: [armbar, triangle-choke]
---
# Closed Guard
""",
        encoding="utf-8",
    )

    open_question_page = repo / "kb" / "open-questions" / "missing-drill-detail.md"
    open_question_page.parent.mkdir(parents=True, exist_ok=True)
    open_question_page.write_text(
        """---
id: missing-drill-detail
type: open-question
title: Missing Drill Detail
status: unresolved
confidence: 0.2
source_refs: []
related_pages: []
---
# Missing Drill Detail
""",
        encoding="utf-8",
    )

    conflict_page = repo / "kb" / "concepts" / "conflicting-terminology.md"
    conflict_page.write_text(
        """---
id: conflicting-terminology
type: concept
title: Conflicting Terminology
status: conflict
confidence: 0.4
source_refs:
- source-overview#chunk-002
related_pages: []
---
# Conflicting Terminology
""",
        encoding="utf-8",
    )

    subprocess.run([sys.executable, str(REBUILD_SCRIPT), str(repo)], check=True)

    index_text = (repo / "kb" / "index.md").read_text(encoding="utf-8")
    gap_report_text = (repo / "generated" / "reports" / "gap-report.md").read_text(encoding="utf-8")
    conflict_report_text = (repo / "generated" / "reports" / "conflict-report.md").read_text(encoding="utf-8")
    improvement_report_text = (repo / "generated" / "reports" / "improvement-report.md").read_text(encoding="utf-8")
    link_map = json.loads((repo / ".kb-state" / "link-map.json").read_text(encoding="utf-8"))

    assert "- [Closed Guard](concepts/closed-guard.md) (`confidence: 0.90`, `status: active`)" in index_text
    assert "- [Missing Drill Detail](../../kb/open-questions/missing-drill-detail.md) (`type: open-question`, `confidence: 0.20`)" in gap_report_text
    assert "- [Conflicting Terminology](../../kb/concepts/conflicting-terminology.md) (`confidence: 0.40`)" in conflict_report_text
    assert (
        "- Add or refine source material for [Missing Drill Detail](../../kb/open-questions/missing-drill-detail.md) "
        "because its current confidence is 0.20."
    ) in improvement_report_text
    assert link_map["closed-guard"]["path"] == "kb/concepts/closed-guard.md"
    assert link_map["closed-guard"]["related_pages"] == ["armbar", "triangle-choke"]
    assert isinstance(link_map["closed-guard"]["related_pages"], list)
    assert link_map["closed-guard"]["source_refs"] == ["source-compendium#chunk-001", "source-compendium#chunk-009"]
    assert isinstance(link_map["closed-guard"]["source_refs"], list)
    assert link_map["closed-guard"]["type"] == "concept"


def test_rebuild_indexes_fails_loudly_when_frontmatter_is_missing(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"
    assert REBUILD_SCRIPT.exists(), f"missing script: {REBUILD_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    invalid_page = repo / "kb" / "concepts" / "missing-frontmatter.md"
    invalid_page.parent.mkdir(parents=True, exist_ok=True)
    invalid_page.write_text("# Missing Frontmatter\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(REBUILD_SCRIPT), str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "missing or invalid frontmatter" in result.stderr
    assert "kb/concepts/missing-frontmatter.md" in result.stderr
