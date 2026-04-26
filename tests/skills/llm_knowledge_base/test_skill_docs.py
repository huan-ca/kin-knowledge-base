from pathlib import Path


SKILL = Path("skills/llm-knowledge-base/SKILL.md")
REPORT_TEMPLATE = Path("skills/llm-knowledge-base/assets/templates/pages/report.md")
KNOWLEDGE_PAGE_TEMPLATE = Path("skills/llm-knowledge-base/assets/templates/pages/knowledge-page.md")
REFERENCES = [
    Path("skills/llm-knowledge-base/references/repo-contract.md"),
    Path("skills/llm-knowledge-base/references/page-types.md"),
    Path("skills/llm-knowledge-base/references/provenance-and-confidence.md"),
    Path("skills/llm-knowledge-base/references/output-patterns.md"),
]


def test_skill_doc_is_concrete_and_placeholder_free():
    text = SKILL.read_text(encoding="utf-8")
    assert "TODO" not in text
    assert "raw/" in text
    assert "kb/" in text
    assert "jobs/" in text
    assert "generated/" in text
    assert "generated/<job-name>/" in text
    assert ".kb-state/" in text
    assert "update_manifest.py" in text
    assert "plan_ingestion.py" in text
    assert "rebuild_indexes.py" in text
    assert "generated/reports/improvement-report.md" in text
    assert "If the request needs facts the KB does not support" in text
    assert "`fact`, `inference`, `editorial-normalization`, and `open-question`" in text
    assert "never writes back into `kb/`" in text or "never write back into `kb/`" in text


def test_reference_docs_exist():
    for reference_path in REFERENCES:
        assert reference_path.exists(), reference_path


def test_report_template_scaffolds_output_requirements():
    text = REPORT_TEMPLATE.read_text(encoding="utf-8")
    assert "## Source Basis" in text
    assert "## Confidence" in text
    assert "## Missing Prerequisites" in text


def test_shared_knowledge_page_template_leaves_page_type_configurable():
    text = KNOWLEDGE_PAGE_TEMPLATE.read_text(encoding="utf-8")
    assert "type: {{ page_type }}" in text
    assert "type: concept" not in text
