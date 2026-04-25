import sys
from pathlib import Path

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
