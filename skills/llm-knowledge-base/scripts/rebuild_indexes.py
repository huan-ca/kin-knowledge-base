from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_dir, iter_markdown_files, parse_frontmatter, parse_scalar, write_json, write_text


UNIVERSAL_PAGE_TYPES = {
    "source",
    "concept",
    "procedure",
    "glossary-term",
    "decision",
    "open-question",
    "report",
}
DEFAULT_REQUIRED_METADATA_FIELDS = {"id", "type", "title", "status", "confidence"}


def load_repo_policy(repo_root: Path) -> tuple[set[str], set[str]]:
    config_path = repo_root / "knowledge-base.yaml"
    if not config_path.exists():
        raise ValueError(f"missing repo policy file: {config_path.name}")

    list_fields = {
        "canonical_domain_types": [],
        "required_page_metadata": [],
    }
    current_list_key: str | None = None

    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if not raw_line.startswith((" ", "\t")):
            current_list_key = None
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if key not in list_fields:
                continue
            if value:
                parsed_value = parse_scalar(value)
                if not isinstance(parsed_value, list):
                    raise ValueError(f"{key} must be a list in {config_path.name}")
                list_fields[key] = parsed_value
                continue
            current_list_key = key
            continue

        if current_list_key and stripped.startswith("- "):
            list_fields[current_list_key].append(parse_scalar(stripped[2:]))

    domain_page_types = {
        item for item in list_fields["canonical_domain_types"] if isinstance(item, str) and item
    }
    required_metadata = DEFAULT_REQUIRED_METADATA_FIELDS | {
        item for item in list_fields["required_page_metadata"] if isinstance(item, str) and item
    }
    return required_metadata, UNIVERSAL_PAGE_TYPES | domain_page_types


def validate_page_metadata(
    metadata: dict,
    relative_path: str,
    required_metadata: set[str],
    allowed_page_types: set[str],
) -> dict:
    missing_fields = [field for field in sorted(required_metadata) if field not in metadata]
    if missing_fields:
        missing_field = missing_fields[0]
        raise ValueError(f"missing required metadata field '{missing_field}' in {relative_path}")

    page_id = metadata.get("id")
    if not isinstance(page_id, str):
        raise ValueError(f"id must be a string in {relative_path}")

    page_type = metadata.get("type")
    if not isinstance(page_type, str):
        raise ValueError(f"type must be a string in {relative_path}")
    if page_type not in allowed_page_types:
        allowed_types_text = ", ".join(f"'{page_type_name}'" for page_type_name in sorted(allowed_page_types))
        raise ValueError(
            f"unknown page type '{page_type}' in {relative_path}; allowed page types: {allowed_types_text}"
        )

    title = metadata.get("title")
    if not isinstance(title, str):
        raise ValueError(f"title must be a string in {relative_path}")

    status = metadata.get("status")
    if not isinstance(status, str):
        raise ValueError(f"status must be a string in {relative_path}")

    source_refs = metadata.get("source_refs", [])
    if not isinstance(source_refs, list):
        raise ValueError(f"source_refs must be a list in {relative_path}")

    related_pages = metadata.get("related_pages", [])
    if not isinstance(related_pages, list):
        raise ValueError(f"related_pages must be a list in {relative_path}")

    raw_confidence = metadata.get("confidence")
    try:
        confidence = float(raw_confidence)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"confidence must be numeric in {relative_path}") from exc

    return {
        "id": page_id,
        "type": page_type,
        "title": title,
        "status": status,
        "confidence": confidence,
        "source_refs": source_refs,
        "related_pages": related_pages,
    }


def load_pages(kb_root: Path, required_metadata: set[str], allowed_page_types: set[str]) -> list[dict]:
    pages = []
    seen_page_ids: dict[str, str] = {}
    for path in iter_markdown_files(kb_root):
        relative_path = path.relative_to(kb_root.parent).as_posix()
        try:
            metadata, _body = parse_frontmatter(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise ValueError(f"missing or invalid frontmatter in {relative_path}: {exc}") from exc
        if not metadata:
            raise ValueError(f"missing or invalid frontmatter in {relative_path}")
        validated = validate_page_metadata(metadata, relative_path, required_metadata, allowed_page_types)
        existing_path = seen_page_ids.get(validated["id"])
        if existing_path:
            raise ValueError(
                f"duplicate page id '{validated['id']}' found in {existing_path} and {relative_path}"
            )
        seen_page_ids[validated["id"]] = relative_path
        pages.append(
            {
                **validated,
                "path": relative_path,
            }
        )
    return pages


def render_index(pages: list[dict]) -> str:
    grouped: dict[str, list[dict]] = {}
    for page in pages:
        grouped.setdefault(page["type"], []).append(page)

    lines = [
        "# Knowledge Base Index",
        "",
        "## Page Counts",
    ]
    for page_type in sorted(grouped):
        lines.append(f"- `{page_type}`: {len(grouped[page_type])}")

    for page_type in sorted(grouped):
        lines.extend(["", f"## {page_type.title()} Pages"])
        for page in sorted(grouped[page_type], key=lambda item: item["title"]):
            lines.append(
                f"- [{page['title']}]({Path(page['path']).relative_to('kb').as_posix()}) "
                f"(`confidence: {page['confidence']:.2f}`, `status: {page['status']}`)"
            )

    return "\n".join(lines) + "\n"


def render_gap_report(pages: list[dict]) -> str:
    gap_pages = [page for page in pages if page["type"] == "open-question" or page["confidence"] < 0.7]
    lines = [
        "# Gap Report",
        "",
        "## Summary",
        f"- Total gap candidates: {len(gap_pages)}",
        "",
        "## Gap Candidates",
    ]
    for page in gap_pages:
        lines.append(f"- [{page['title']}](../../{page['path']}) (`type: {page['type']}`, `confidence: {page['confidence']:.2f}`)")
    return "\n".join(lines) + "\n"


def render_conflict_report(pages: list[dict]) -> str:
    conflict_pages = [page for page in pages if page["status"] == "conflict"]
    lines = [
        "# Conflict Report",
        "",
        "## Summary",
        f"- Total conflicts: {len(conflict_pages)}",
        "",
        "## Conflicts",
    ]
    for page in conflict_pages:
        lines.append(f"- [{page['title']}](../../{page['path']}) (`confidence: {page['confidence']:.2f}`)")
    return "\n".join(lines) + "\n"


def render_improvement_report(pages: list[dict]) -> str:
    weak_pages = [page for page in pages if page["type"] == "open-question" or page["confidence"] < 0.7]
    lines = [
        "# Improvement Report",
        "",
        "## Source Basis",
    ]
    for page in weak_pages:
        if page["source_refs"]:
            lines.append(
                f"- [{page['title']}](../../{page['path']}): derived from {', '.join(f'`{ref}`' for ref in page['source_refs'])}"
            )
        else:
            lines.append(f"- [{page['title']}](../../{page['path']}): no supporting source refs recorded.")

    lines.extend(
        [
            "",
            "## Confidence",
        ]
    )
    for page in weak_pages:
        lines.append(f"- [{page['title']}](../../{page['path']}): current confidence {page['confidence']:.2f}.")

    lines.extend(
        [
            "",
            "## Missing Prerequisites",
        ]
    )
    for page in weak_pages:
        if page["type"] == "open-question":
            lines.append(f"- [{page['title']}](../../{page['path']}): unresolved question blocks stronger output.")
        elif not page["source_refs"]:
            lines.append(f"- [{page['title']}](../../{page['path']}): missing supporting source refs.")
        else:
            lines.append(f"- [{page['title']}](../../{page['path']}): stronger corroborating evidence is still needed.")

    lines.extend(
        [
            "",
        "## Recommended Improvements",
        ]
    )
    for page in weak_pages:
        lines.append(
            f"- Add or refine source material for [{page['title']}](../../{page['path']}) "
            f"because its current confidence is {page['confidence']:.2f}."
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Rebuild derived indexes and reports from kb markdown pages.")
    parser.add_argument("repo_root", help="Path to the repo root.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    try:
        required_metadata, allowed_page_types = load_repo_policy(repo_root)
        pages = load_pages(repo_root / "kb", required_metadata, allowed_page_types)
    except ValueError as exc:
        raise SystemExit(str(exc))

    write_text(repo_root / "kb" / "index.md", render_index(pages), overwrite=True)

    reports_dir = ensure_dir(repo_root / "generated" / "reports")
    write_text(reports_dir / "gap-report.md", render_gap_report(pages), overwrite=True)
    write_text(reports_dir / "conflict-report.md", render_conflict_report(pages), overwrite=True)
    write_text(reports_dir / "improvement-report.md", render_improvement_report(pages), overwrite=True)

    link_map = {
        page["id"]: {
            "path": page["path"],
            "related_pages": page["related_pages"],
            "source_refs": page["source_refs"],
            "type": page["type"],
        }
        for page in pages
    }
    write_json(repo_root / ".kb-state" / "link-map.json", link_map)


if __name__ == "__main__":
    main()
