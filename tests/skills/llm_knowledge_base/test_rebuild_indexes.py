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
source_refs:
- source-compendium#chunk-001
related_pages:
- armbar
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

    assert "Closed Guard" in index_text
    assert "Missing Drill Detail" in gap_report_text
    assert "Conflicting Terminology" in conflict_report_text
    assert "Add or refine source material" in improvement_report_text
    assert link_map["closed-guard"]["related_pages"] == ["armbar"]
