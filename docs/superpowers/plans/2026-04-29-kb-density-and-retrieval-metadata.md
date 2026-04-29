# KB Density And Retrieval Metadata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Raise the default information density of new KB pages and expose retrieval-oriented page metadata in the KB manifest without rewriting existing KB content.

**Architecture:** Update the markdown page templates so they nudge authors toward richer page bodies, tighten the `llm-knowledge-base` guidance so ingestion preserves more usable detail, and extend rebuild-time metadata parsing so `domain_tags` and `keywords` flow into the KB manifest. Keep the change additive and backward-compatible for existing pages by treating the new retrieval metadata as optional.

**Tech Stack:** Python 3, pytest, markdown templates, repo-local Codex skill docs

---

### Task 1: Cover Retrieval Metadata In Frontmatter Parsing And Rebuild Output

**Files:**
- Modify: `tests/skills/llm_knowledge_base/test_common.py`
- Modify: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`
- Modify later: `skills/llm-knowledge-base/scripts/rebuild_indexes.py`

- [ ] **Step 1: Add a failing frontmatter parsing test for inline `domain_tags` and `keywords`**

```python
def test_parse_frontmatter_parses_inline_domain_tags_and_keywords():
    metadata, _body = parse_frontmatter(
        "---\n"
        "domain_tags: [class-type, pedagogy]\n"
        "keywords: [class structure, lesson flow, behavior management]\n"
        "---\n"
        "Body text\n"
    )

    assert metadata["domain_tags"] == ["class-type", "pedagogy"]
    assert metadata["keywords"] == ["class structure", "lesson flow", "behavior management"]
```

- [ ] **Step 2: Add a failing frontmatter parsing test for indented `keywords` lists**

```python
def test_parse_frontmatter_parses_indented_keywords_list():
    metadata, _body = parse_frontmatter(
        "---\n"
        "keywords:\n"
        "  - closed guard\n"
        "  - guard retention\n"
        "  - posture control\n"
        "---\n"
        "Body text\n"
    )

    assert metadata["keywords"] == ["closed guard", "guard retention", "posture control"]
```

- [ ] **Step 3: Add a failing rebuild test that expects manifest records to include retrieval metadata**

```python
concept_page.write_text(
    \"\"\"---
id: closed-guard
type: concept
title: Closed Guard
status: active
confidence: 0.9
claim_label: fact
source_refs: [source-compendium#chunk-001, source-compendium#chunk-009]
related_pages: [armbar, triangle-choke]
domain_tags: [guard, offensive-cycle]
keywords: [closed guard, posture breaking, hip control]
---
# Closed Guard
\"\"\",
    encoding=\"utf-8\",
)
```

Then extend the assertions:

```python
closed_guard_record = next(page for page in kb_manifest["pages"] if page["id"] == "closed-guard")
assert closed_guard_record["domain_tags"] == ["guard", "offensive-cycle"]
assert closed_guard_record["keywords"] == ["closed guard", "posture breaking", "hip control"]
assert link_map["closed-guard"]["domain_tags"] == ["guard", "offensive-cycle"]
assert link_map["closed-guard"]["keywords"] == ["closed guard", "posture breaking", "hip control"]
```

- [ ] **Step 4: Add a failing rebuild test proving pages without the new fields still succeed**

```python
armbar_record = next(page for page in kb_manifest["pages"] if page["id"] == "armbar")
assert armbar_record["domain_tags"] == []
assert armbar_record["keywords"] == []
```

- [ ] **Step 5: Run the targeted tests to verify failure before implementation**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_common.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q
```

Expected:

```text
FAIL ... KeyError or assertion failure for missing domain_tags/keywords fields
```

- [ ] **Step 6: Commit the red test checkpoint**

```bash
git add tests/skills/llm_knowledge_base/test_common.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py
git commit -m "test: cover kb retrieval metadata fields"
```

### Task 2: Implement Optional Retrieval Metadata In Rebuild Logic

**Files:**
- Modify: `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
- Reuse tests from: `tests/skills/llm_knowledge_base/test_common.py`
- Reuse tests from: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`

- [ ] **Step 1: Extend metadata validation to accept optional list fields**

Add parsing and validation in `validate_page_metadata()` after `related_pages`:

```python
    domain_tags = metadata.get("domain_tags", [])
    if not isinstance(domain_tags, list):
        raise ValueError(f"domain_tags must be a list in {relative_path}")

    keywords = metadata.get("keywords", [])
    if not isinstance(keywords, list):
        raise ValueError(f"keywords must be a list in {relative_path}")
```

Return them from the validated payload:

```python
    return {
        "id": page_id,
        "type": page_type,
        "title": title,
        "status": status,
        "confidence": confidence,
        "claim_label": claim_label,
        "source_refs": source_refs,
        "related_pages": related_pages,
        "domain_tags": domain_tags,
        "keywords": keywords,
    }
```

- [ ] **Step 2: Thread the new fields through loaded pages**

Keep `load_pages()` returning the expanded validated payload:

```python
        pages.append(
            {
                **validated,
                "path": relative_path,
            }
        )
```

No extra transformation should be needed once `validated` carries `domain_tags` and `keywords`.

- [ ] **Step 3: Add the retrieval metadata to the KB manifest**

Update `build_kb_manifest()`:

```python
    manifest_pages = [
        {
            "id": page["id"],
            "type": page["type"],
            "title": page["title"],
            "status": page["status"],
            "confidence": page["confidence"],
            "path": page["path"],
            "claim_label": page["claim_label"],
            "source_refs": page["source_refs"],
            "related_pages": page["related_pages"],
            "domain_tags": page["domain_tags"],
            "keywords": page["keywords"],
        }
        for page in sorted(pages, key=lambda item: item["id"])
    ]
```

- [ ] **Step 4: Add the retrieval metadata to `.kb-state/link-map.json`**

Update the `link_map` payload in `main()`:

```python
    link_map = {
        page["id"]: {
            "path": page["path"],
            "related_pages": page["related_pages"],
            "source_refs": page["source_refs"],
            "type": page["type"],
            "domain_tags": page["domain_tags"],
            "keywords": page["keywords"],
        }
        for page in pages
    }
```

- [ ] **Step 5: Run the targeted tests to verify the new behavior passes**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_common.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q
```

Expected:

```text
... all selected tests pass
```

- [ ] **Step 6: Commit the implementation checkpoint**

```bash
git add skills/llm-knowledge-base/scripts/rebuild_indexes.py tests/skills/llm_knowledge_base/test_common.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py
git commit -m "feat: expose kb retrieval metadata in rebuild outputs"
```

### Task 3: Raise Template Density Defaults

**Files:**
- Modify: `skills/llm-knowledge-base/assets/templates/pages/knowledge-page.md`
- Modify: `skills/llm-knowledge-base/assets/templates/pages/domain-page.md`
- Optional verification target: `tests/skills/llm_knowledge_base/test_init_repo.py`

- [ ] **Step 1: Rewrite `knowledge-page.md` to the richer baseline structure**

Replace the body template with:

```md
---
id: {{ page_id }}
type: {{ page_type }}
title: "{{ title }}"
status: draft
confidence: 0.5
claim_label: fact
source_refs:
- source-{{ source_slug }}#chunk-001
related_pages: []
domain_tags: []
keywords: []
---
# {{ title }}

## Definition
[State the claim conservatively and directly.]

## Detailed Notes
- [Preserve distinctions, supporting detail, and context from the source]
- [Add additional usable detail instead of compressing everything into one sentence]

<!-- ## Operational Implications
- [Only include when the page affects how someone should act, teach, or structure work]
-->

<!-- ## Examples or Variants
- [Only include when examples, forms, or program/age variants materially improve understanding]
-->

<!-- ## Constraints or Safety Notes
- [Only include when limits, cautions, safety concerns, or sequencing boundaries matter]
-->

## Related Pages
- [[related-page]]

## Gaps
- [What remains unclear or under-specified]
```

- [ ] **Step 2: Rewrite `domain-page.md` to the same richer baseline**

Replace the body template with:

```md
---
id: {{ page_id }}
type: {{ domain_type }}
title: "{{ title }}"
status: draft
confidence: 0.5
claim_label: fact
source_refs:
- source-{{ source_slug }}#chunk-001
related_pages: []
domain_tags:
- {{ domain_type }}
keywords: []
---
# {{ title }}

## Definition
[Describe the domain-specific item conservatively with explicit provenance.]

## Detailed Notes
- [Preserve distinctions, supporting detail, and operational context from the source]
- [Capture the parts a generator or reader would actually need later]

<!-- ## Operational Implications
- [Only include when this changes how a coach, student, or operator should act]
-->

<!-- ## Examples or Variants
- [Only include when examples, age bands, or contextual variants matter]
-->

<!-- ## Constraints or Safety Notes
- [Only include when this topic has limits, cautions, or safety boundaries]
-->

## Related Pages
- [[related-page]]

## Gaps
- [What remains unclear]
```

- [ ] **Step 3: Add or update a test only if template coverage currently exists**

If `tests/skills/llm_knowledge_base/test_init_repo.py` already asserts template text, add explicit checks such as:

```python
assert "## Detailed Notes" in template_text
assert "keywords: []" in template_text
assert "## Gaps" in template_text
```

If no template assertions exist, skip adding a new brittle test and rely on the direct file diff plus downstream skill guidance tests.

- [ ] **Step 4: Run the relevant tests**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_init_repo.py tests/skills/llm_knowledge_base/test_common.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py -q
```

Expected:

```text
... all selected tests pass
```

- [ ] **Step 5: Commit the template checkpoint**

```bash
git add skills/llm-knowledge-base/assets/templates/pages/knowledge-page.md skills/llm-knowledge-base/assets/templates/pages/domain-page.md tests/skills/llm_knowledge_base/test_init_repo.py
git commit -m "feat: raise kb page template density defaults"
```

### Task 4: Tighten Skill Guidance Around Dense Pages

**Files:**
- Modify: `skills/llm-knowledge-base/SKILL.md`

- [ ] **Step 1: Expand the normalization guidance to explicitly reject thin summaries**

Update the `Normalize knowledge into kb/` section so it includes language like:

```md
- Preserve distinctions, examples, and contextual implications when the source supports them.
- Do not collapse rich source material into thin summary pages unless the user explicitly asks for a lighter pass.
- Treat each derived page as a retrieval unit that should be strong enough to support downstream generation with specificity.
```

- [ ] **Step 2: Add guidance for optional practice-oriented sections**

Add a short subsection or bullets under ingestion density guidance:

```md
- Use `Operational Implications` when the page affects behavior, teaching, or process.
- Use `Examples or Variants` when concrete forms or age/program variants improve understanding.
- Use `Constraints or Safety Notes` when limits, cautions, or sequencing boundaries materially affect use.
- These sections are conditional, not mandatory on every page.
```

- [ ] **Step 3: Add guidance for retrieval metadata authoring**

Add a short guidance block:

```md
- Use `domain_tags` for short curated topic labels.
- Use `keywords` for retrieval terms, aliases, common phrases, and likely search vocabulary.
- Prefer a few strong retrieval terms over long noisy lists.
```

- [ ] **Step 4: Sanity-check the skill document for contradictions with the new templates**

Run:

```bash
rg -n "Canonical Statement|Supporting Evidence|Key Details|Detailed Notes|keywords|domain_tags" skills/llm-knowledge-base/SKILL.md skills/llm-knowledge-base/assets/templates/pages
```

Expected:

```text
Template and skill terminology now align on Detailed Notes / Gaps / retrieval metadata
```

- [ ] **Step 5: Commit the guidance checkpoint**

```bash
git add skills/llm-knowledge-base/SKILL.md
git commit -m "docs: strengthen kb density and retrieval guidance"
```

### Task 5: Final Verification

**Files:**
- Verify: `skills/llm-knowledge-base/scripts/rebuild_indexes.py`
- Verify: `skills/llm-knowledge-base/SKILL.md`
- Verify: `skills/llm-knowledge-base/assets/templates/pages/knowledge-page.md`
- Verify: `skills/llm-knowledge-base/assets/templates/pages/domain-page.md`
- Verify: `tests/skills/llm_knowledge_base/test_common.py`
- Verify: `tests/skills/llm_knowledge_base/test_rebuild_indexes.py`
- Verify: `tests/skills/llm_knowledge_base/test_init_repo.py`

- [ ] **Step 1: Run the KB verification suite**

Run:

```bash
pytest tests/skills/llm_knowledge_base/test_common.py tests/skills/llm_knowledge_base/test_rebuild_indexes.py tests/skills/llm_knowledge_base/test_init_repo.py -q
```

Expected:

```text
all selected tests pass
```

- [ ] **Step 2: Run bytecode verification for the rebuild script**

Run:

```bash
python3 -m py_compile skills/llm-knowledge-base/scripts/rebuild_indexes.py
```

Expected:

```text
no output
```

- [ ] **Step 3: Inspect the final diff for scope control**

Run:

```bash
git diff --stat HEAD~4..HEAD
```

Expected:

```text
Only the templates, skill guidance, rebuild script, and targeted tests changed
```

- [ ] **Step 4: Create the final implementation commit if needed**

If any verification-only fixes were made after earlier commits:

```bash
git add skills/llm-knowledge-base/assets/templates/pages/knowledge-page.md \
  skills/llm-knowledge-base/assets/templates/pages/domain-page.md \
  skills/llm-knowledge-base/SKILL.md \
  skills/llm-knowledge-base/scripts/rebuild_indexes.py \
  tests/skills/llm_knowledge_base/test_common.py \
  tests/skills/llm_knowledge_base/test_rebuild_indexes.py \
  tests/skills/llm_knowledge_base/test_init_repo.py
git commit -m "chore: finalize kb density and retrieval metadata updates"
```

- [ ] **Step 5: Report completion with explicit non-goals preserved**

The handoff should explicitly state:

```text
- Existing KB pages were not rewritten
- Ingestion/generation was not rerun as part of this change
- Retrieval metadata is optional and backward-compatible
```
