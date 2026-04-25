from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_dir, iter_markdown_files, parse_frontmatter, write_json, write_text


def load_pages(kb_root: Path) -> list[dict]:
    pages = []
    for path in iter_markdown_files(kb_root):
        metadata, _body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if not metadata:
            continue
        pages.append(
            {
                "id": metadata.get("id", path.stem),
                "type": metadata.get("type", "unknown"),
                "title": metadata.get("title", path.stem.replace("-", " ").title()),
                "status": metadata.get("status", "draft"),
                "confidence": float(metadata.get("confidence", 0.0)),
                "source_refs": metadata.get("source_refs", []),
                "related_pages": metadata.get("related_pages", []),
                "path": path.relative_to(kb_root.parent).as_posix(),
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
    pages = load_pages(repo_root / "kb")

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
