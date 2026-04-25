import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path("skills/llm-knowledge-base/scripts").resolve()
sys.path.insert(0, str(SCRIPTS_DIR))

from common import parse_frontmatter


def test_parse_frontmatter_preserves_inline_empty_lists():
    metadata, body = parse_frontmatter(
        "---\n"
        "source_refs: []\n"
        "related_pages: []\n"
        "title: \"Example\"\n"
        "---\n"
        "Body text\n"
    )

    assert metadata["source_refs"] == []
    assert metadata["related_pages"] == []
    assert metadata["title"] == "Example"
    assert body == "Body text\n"


def test_parse_frontmatter_parses_inline_non_empty_lists():
    metadata, _body = parse_frontmatter(
        "---\n"
        "source_refs: [source-a#chunk-001, source-b#chunk-002]\n"
        "related_pages: [armbar, triangle-choke]\n"
        "---\n"
        "Body text\n"
    )

    assert metadata["source_refs"] == ["source-a#chunk-001", "source-b#chunk-002"]
    assert metadata["related_pages"] == ["armbar", "triangle-choke"]


def test_parse_frontmatter_rejects_non_key_value_lines():
    with pytest.raises(ValueError, match="invalid frontmatter line: not valid yaml line"):
        parse_frontmatter(
            "---\n"
            "title: Example\n"
            "not valid yaml line\n"
            "---\n"
            "Body text\n"
        )


def test_parse_frontmatter_rejects_stray_list_items_without_active_key():
    with pytest.raises(ValueError, match="invalid frontmatter list item: - stray-item"):
        parse_frontmatter(
            "---\n"
            "- stray-item\n"
            "---\n"
            "Body text\n"
        )
