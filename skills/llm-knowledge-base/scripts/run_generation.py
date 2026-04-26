from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT_FOR_IMPORTS = Path(__file__).resolve().parents[3]
if str(REPO_ROOT_FOR_IMPORTS) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT_FOR_IMPORTS))

from repo_generators.registry import load_generator

from common import git_commit, parse_frontmatter, read_simple_yaml, write_json


JOB_REQUIRED_FIELDS = ("id", "title", "generation_targets", "status", "transient")
JOB_REQUIRED_SECTIONS = ("Purpose", "Instructions", "Q&A", "Notes")


def parse_markdown_sections(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_section: str | None = None

    for line in body.splitlines():
        if line.startswith("## "):
            current_section = line[3:].strip()
            sections[current_section] = []
            continue
        if current_section is not None:
            sections[current_section].append(line)

    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


def load_job_spec(repo_root: Path, job_name: str, default_generator: str | None = None) -> tuple[dict, dict]:
    job_root = repo_root / "jobs" / job_name
    job_yaml_path = job_root / "job.yaml"
    if not job_yaml_path.exists():
        raise ValueError(f"missing job spec: {job_yaml_path}")

    job_spec = read_simple_yaml(job_yaml_path)
    missing_fields = [field for field in JOB_REQUIRED_FIELDS if field not in job_spec]
    if missing_fields:
        raise ValueError(f"job spec is missing required fields: {', '.join(missing_fields)}")
    if "generator" not in job_spec:
        if not default_generator:
            raise ValueError("job spec is missing required field: generator")
        job_spec["generator"] = default_generator

    targets = job_spec.get("generation_targets")
    if not isinstance(targets, list):
        raise ValueError("job spec generation_targets must be a list")

    notes_path = job_root / "notes.md"
    notes_sections = {section: "" for section in JOB_REQUIRED_SECTIONS}
    if notes_path.exists():
        _, body = parse_frontmatter(notes_path.read_text(encoding="utf-8"))
        notes_sections.update(parse_markdown_sections(body))
    missing_sections = [section for section in JOB_REQUIRED_SECTIONS if section not in notes_sections]
    if missing_sections:
        raise ValueError(f"job notes are missing required sections: {', '.join(missing_sections)}")

    return job_spec, {
        "job_name": job_name,
        "job_root": job_root,
        "job_yaml_path": job_yaml_path,
        "notes_path": notes_path if notes_path.exists() else None,
        "notes_sections": notes_sections,
    }


def write_run_metadata(repo_root: Path, output_root: Path, job_spec: dict, job_context: dict, result: dict) -> None:
    metadata = {
        "job_name": job_context["job_name"],
        "generator": job_spec["generator"],
        "git_commit": git_commit(repo_root),
        "job_spec_path": job_context["job_yaml_path"].relative_to(repo_root).as_posix(),
        "notes_path": job_context["notes_path"].relative_to(repo_root).as_posix() if job_context["notes_path"] else None,
        "generation_targets": job_spec.get("generation_targets", []),
        "inputs": job_spec.get("inputs", {}),
        "options": job_spec.get("options", {}),
        "outputs": result.get("outputs", []),
        "warnings": result.get("warnings", []),
        "new_facts_count": result.get("new_facts_count", 0),
    }
    write_json(output_root / "_meta" / "run.json", metadata)


def run_generation(repo_root: Path, job_name: str, default_generator: str | None = None) -> dict:
    job_spec, job_context = load_job_spec(repo_root, job_name, default_generator=default_generator)
    generator = load_generator(job_spec["generator"])
    result = generator.generate(repo_root, job_spec, job_context)
    output_root = repo_root / "generated" / job_name
    write_run_metadata(repo_root, output_root, job_spec, job_context, result)
    return result


def main(default_generator: str | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run a named generation job from jobs/<job-name>/job.yaml.")
    parser.add_argument("repo_root", help="Path to the repo root.")
    parser.add_argument("--job-name", required=True, help="Job name under jobs/<job-name>/job.yaml.")
    args = parser.parse_args()

    try:
        run_generation(Path(args.repo_root).resolve(), args.job_name, default_generator=default_generator)
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
