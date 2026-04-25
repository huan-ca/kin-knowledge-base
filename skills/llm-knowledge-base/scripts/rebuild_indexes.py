from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_dir, iter_markdown_files, parse_frontmatter, write_json, write_text


def validate_page_metadata(metadata: dict, relative_path: str) -> dict:
    page_id = metadata.get("id")
    if not isinstance(page_id, str):
        raise ValueError(f"id must be a string in {relative_path}")

    source_refs = metadata.get("source_refs", [])
    if not isinstance(source_refs, list):
        raise ValueError(f"source_refs must be a list in {relative_path}")

    related_pages = metadata.get("related_pages", [])
    if not isinstance(related_pages, list):
        raise ValueError(f"related_pages must be a list in {relative_path}")

    raw_confidence = metadata.get("confidence", 0.0)
    try:
        confidence = float(raw_confidence)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"confidence must be numeric in {relative_path}") from exc

    return {
        "id": page_id,
        "type": metadata.get("type", "unknown"),
        "title": metadata.get("title", page_id.replace("-", " ").title()),
        "status": metadata.get("status", "draft"),
        "confidence": confidence,
        "source_refs": source_refs,
        "related_pages": related_pages,
    }


def load_pages(kb_root: Path) -> list[dict]:
    pages = []
    for path in iter_markdown_files(kb_root):
        relative_path = path.relative_to(kb_root.parent).as_posix()
        try:
            metadata, _body = parse_frontmatter(path.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise ValueError(f"missing or invalid frontmatter in {relative_path}: {exc}") from exc
        if not metadata:
            raise ValueError(f"missing or invalid frontmatter in {relative_path}")
        validated = validate_page_metadata(metadata, relative_path)
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
        "## Recommended Improvements",
    ]
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
        pages = load_pages(repo_root / "kb")
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
