import json
import subprocess
import sys
from pathlib import Path

import pytest

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
    assert "## Source Basis" in improvement_report_text
    assert "## Confidence" in improvement_report_text
    assert "## Missing Prerequisites" in improvement_report_text
    assert link_map["closed-guard"]["path"] == "kb/concepts/closed-guard.md"
    assert link_map["closed-guard"]["related_pages"] == ["armbar", "triangle-choke"]
    assert isinstance(link_map["closed-guard"]["related_pages"], list)
    assert link_map["closed-guard"]["source_refs"] == ["source-compendium#chunk-001", "source-compendium#chunk-009"]
    assert isinstance(link_map["closed-guard"]["source_refs"], list)
    assert link_map["closed-guard"]["type"] == "concept"


def test_rebuild_indexes_includes_nested_index_and_readme_pages_without_re_reading_generated_top_level_index(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"
    assert REBUILD_SCRIPT.exists(), f"missing script: {REBUILD_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    nested_index_page = repo / "kb" / "concepts" / "index.md"
    nested_index_page.parent.mkdir(parents=True, exist_ok=True)
    nested_index_page.write_text(
        """---
id: concepts-overview
type: concept
title: Concepts Overview
status: active
confidence: 0.8
source_refs: []
related_pages: []
---
# Concepts Overview
""",
        encoding="utf-8",
    )

    nested_readme_page = repo / "kb" / "foo" / "README.md"
    nested_readme_page.parent.mkdir(parents=True, exist_ok=True)
    nested_readme_page.write_text(
        """---
id: foo-readme
type: procedure
title: Foo Readme
status: active
confidence: 0.85
source_refs: []
related_pages: []
---
# Foo Readme
""",
        encoding="utf-8",
    )

    subprocess.run([sys.executable, str(REBUILD_SCRIPT), str(repo)], check=True)
    subprocess.run([sys.executable, str(REBUILD_SCRIPT), str(repo)], check=True)

    index_text = (repo / "kb" / "index.md").read_text(encoding="utf-8")
    link_map = json.loads((repo / ".kb-state" / "link-map.json").read_text(encoding="utf-8"))

    assert "- [Concepts Overview](concepts/index.md) (`confidence: 0.80`, `status: active`)" in index_text
    assert "- [Foo Readme](foo/README.md) (`confidence: 0.85`, `status: active`)" in index_text
    assert link_map["concepts-overview"]["path"] == "kb/concepts/index.md"
    assert link_map["foo-readme"]["path"] == "kb/foo/README.md"


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


def test_rebuild_indexes_fails_loudly_when_frontmatter_contains_invalid_line(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"
    assert REBUILD_SCRIPT.exists(), f"missing script: {REBUILD_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    invalid_page = repo / "kb" / "concepts" / "invalid-frontmatter-line.md"
    invalid_page.parent.mkdir(parents=True, exist_ok=True)
    invalid_page.write_text(
        """---
id: invalid-frontmatter-line
type: concept
title: Invalid Frontmatter Line
not valid yaml line
---
# Invalid Frontmatter Line
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(REBUILD_SCRIPT), str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "missing or invalid frontmatter in kb/concepts/invalid-frontmatter-line.md" in result.stderr
    assert "invalid frontmatter line: not valid yaml line" in result.stderr


@pytest.mark.parametrize("missing_field", ["type", "title", "status", "confidence"])
def test_rebuild_indexes_requires_all_configured_metadata_fields(tmp_path, missing_field):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"
    assert REBUILD_SCRIPT.exists(), f"missing script: {REBUILD_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    metadata = {
        "id": "missing-required-metadata",
        "type": "concept",
        "title": "Missing Required Metadata",
        "status": "active",
        "confidence": "0.5",
        "source_refs": "[]",
        "related_pages": "[]",
    }
    del metadata[missing_field]
    frontmatter = "\n".join(f"{key}: {value}" for key, value in metadata.items())

    invalid_page = repo / "kb" / "concepts" / "missing-required-metadata.md"
    invalid_page.parent.mkdir(parents=True, exist_ok=True)
    invalid_page.write_text(f"---\n{frontmatter}\n---\n# Invalid Page\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(REBUILD_SCRIPT), str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert f"missing required metadata field '{missing_field}' in kb/concepts/missing-required-metadata.md" in result.stderr


def test_rebuild_indexes_rejects_unknown_page_types(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"
    assert REBUILD_SCRIPT.exists(), f"missing script: {REBUILD_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    invalid_page = repo / "kb" / "concepts" / "unknown-page-type.md"
    invalid_page.parent.mkdir(parents=True, exist_ok=True)
    invalid_page.write_text(
        """---
id: unknown-page-type
type: alien-taxonomy
title: Unknown Page Type
status: active
confidence: 0.5
source_refs: []
related_pages: []
---
# Unknown Page Type
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(REBUILD_SCRIPT), str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "unknown page type 'alien-taxonomy' in kb/concepts/unknown-page-type.md" in result.stderr
    assert "allowed page types:" in result.stderr


def test_rebuild_indexes_rejects_duplicate_page_ids(tmp_path):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"
    assert REBUILD_SCRIPT.exists(), f"missing script: {REBUILD_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    page_one = repo / "kb" / "concepts" / "duplicate-id-one.md"
    page_one.parent.mkdir(parents=True, exist_ok=True)
    page_one.write_text(
        """---
id: duplicate-page-id
type: concept
title: Duplicate Page Id One
status: active
confidence: 0.6
source_refs: []
related_pages: []
---
# Duplicate Page Id One
""",
        encoding="utf-8",
    )

    page_two = repo / "kb" / "procedures" / "duplicate-id-two.md"
    page_two.parent.mkdir(parents=True, exist_ok=True)
    page_two.write_text(
        """---
id: duplicate-page-id
type: procedure
title: Duplicate Page Id Two
status: active
confidence: 0.7
source_refs: []
related_pages: []
---
# Duplicate Page Id Two
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(REBUILD_SCRIPT), str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "duplicate page id 'duplicate-page-id'" in result.stderr
    assert "kb/concepts/duplicate-id-one.md" in result.stderr
    assert "kb/procedures/duplicate-id-two.md" in result.stderr


@pytest.mark.parametrize(
    ("page_name", "frontmatter_body", "expected_error"),
    [
        (
            "source-refs-not-list",
            "id: source-refs-not-list\n"
            "type: concept\n"
            "title: Source Refs Not List\n"
            "status: active\n"
            "confidence: 0.5\n"
            "source_refs: source-a#chunk-001\n"
            "related_pages: []\n",
            "source_refs must be a list in kb/concepts/source-refs-not-list.md",
        ),
        (
            "related-pages-not-list",
            "id: related-pages-not-list\n"
            "type: concept\n"
            "title: Related Pages Not List\n"
            "status: active\n"
            "confidence: 0.5\n"
            "source_refs: []\n"
            "related_pages: armbar\n",
            "related_pages must be a list in kb/concepts/related-pages-not-list.md",
        ),
        (
            "id-not-string",
            "id:\n"
            "- stray-item\n"
            "type: concept\n"
            "title: Id Not String\n"
            "status: active\n"
            "confidence: 0.5\n"
            "source_refs: []\n"
            "related_pages: []\n",
            "id must be a string in kb/concepts/id-not-string.md",
        ),
        (
            "confidence-not-numeric",
            "id: confidence-not-numeric\n"
            "type: concept\n"
            "title: Confidence Not Numeric\n"
            "status: active\n"
            "confidence: very-sure\n"
            "source_refs: []\n"
            "related_pages: []\n",
            "confidence must be numeric in kb/concepts/confidence-not-numeric.md",
        ),
        (
            "type-not-string",
            "id: type-not-string\n"
            "type:\n"
            "- concept\n"
            "title: Type Not String\n"
            "status: active\n"
            "confidence: 0.5\n"
            "source_refs: []\n"
            "related_pages: []\n",
            "type must be a string in kb/concepts/type-not-string.md",
        ),
        (
            "title-not-string",
            "id: title-not-string\n"
            "type: concept\n"
            "title:\n"
            "- Bad Title\n"
            "status: active\n"
            "confidence: 0.5\n"
            "source_refs: []\n"
            "related_pages: []\n",
            "title must be a string in kb/concepts/title-not-string.md",
        ),
        (
            "status-not-string",
            "id: status-not-string\n"
            "type: concept\n"
            "title: Status Not String\n"
            "status:\n"
            "- active\n"
            "confidence: 0.5\n"
            "source_refs: []\n"
            "related_pages: []\n",
            "status must be a string in kb/concepts/status-not-string.md",
        ),
    ],
)
def test_rebuild_indexes_validates_frontmatter_schema(tmp_path, page_name, frontmatter_body, expected_error):
    assert INIT_SCRIPT.exists(), f"missing script: {INIT_SCRIPT}"
    assert REBUILD_SCRIPT.exists(), f"missing script: {REBUILD_SCRIPT}"

    repo = tmp_path / "demo-repo"
    repo.mkdir()
    subprocess.run([sys.executable, str(INIT_SCRIPT), str(repo)], check=True)

    invalid_page = repo / "kb" / "concepts" / f"{page_name}.md"
    invalid_page.parent.mkdir(parents=True, exist_ok=True)
    invalid_page.write_text(f"---\n{frontmatter_body}---\n# Invalid Page\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(REBUILD_SCRIPT), str(repo)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert expected_error in result.stderr
