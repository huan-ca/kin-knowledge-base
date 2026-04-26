from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


def skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def templates_root() -> Path:
    return skill_root() / "assets" / "templates"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_text(path: Path, content: str, overwrite: bool = False) -> None:
    ensure_dir(path.parent)
    if path.exists() and not overwrite:
        return
    path.write_text(content, encoding="utf-8")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_commit(repo_root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(item) for item in inner.split(",")]
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value in {"true", "false"}:
        return value == "true"
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def parse_simple_yaml(text: str) -> dict[str, Any]:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()

    def indentation(line: str) -> int:
        return len(line) - len(line.lstrip(" "))

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        mapping: dict[str, Any] = {}
        sequence: list[Any] | None = None

        while index < len(lines):
            raw = lines[index]
            if not raw.strip():
                index += 1
                continue
            current_indent = indentation(raw)
            if current_indent < indent:
                break
            if current_indent > indent:
                raise ValueError(f"invalid indentation: {raw}")

            stripped = raw.strip()
            if stripped.startswith("- "):
                if mapping:
                    raise ValueError("cannot mix list items and mapping at same indentation")
                if sequence is None:
                    sequence = []
                item_text = stripped[2:].strip()
                if not item_text:
                    value, index = parse_block(index + 1, indent + 2)
                    sequence.append(value)
                    continue
                sequence.append(parse_scalar(item_text))
                index += 1
                continue

            if sequence is not None:
                raise ValueError("cannot mix mapping entries and list items at same indentation")
            if ":" not in stripped:
                raise ValueError(f"invalid yaml line: {raw}")
            key, remainder = stripped.split(":", 1)
            remainder = remainder.strip()
            if remainder:
                mapping[key] = parse_scalar(remainder)
                index += 1
                continue

            next_index = index + 1
            while next_index < len(lines) and not lines[next_index].strip():
                next_index += 1
            if next_index >= len(lines) or indentation(lines[next_index]) <= indent:
                mapping[key] = {}
                index = next_index
                continue

            value, index = parse_block(next_index, indent + 2)
            mapping[key] = value

        if sequence is not None:
            return sequence, index
        return mapping, index

    parsed, _ = parse_block(0, 0)
    if not isinstance(parsed, dict):
        raise ValueError("top-level yaml payload must be a mapping")
    return parsed


def read_simple_yaml(path: Path) -> dict[str, Any]:
    return parse_simple_yaml(path.read_text(encoding="utf-8"))


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if not text.startswith("---\n"):
        return {}, text

    _, remainder = text.split("---\n", 1)
    header, body = remainder.split("\n---\n", 1)

    metadata: dict[str, Any] = {}
    current_key: str | None = None

    for raw_line in header.splitlines():
        line = raw_line.rstrip()
        stripped = line.lstrip()
        if not line:
            continue
        if stripped.startswith("- "):
            if not current_key:
                raise ValueError(f"invalid frontmatter list item: {stripped}")
            metadata.setdefault(current_key, []).append(parse_scalar(stripped[2:]))
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value:
            metadata[key] = parse_scalar(value)
            current_key = None
        else:
            metadata[key] = []
            current_key = key

    return metadata, body


def iter_markdown_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        path
        for path in root.rglob("*.md")
        if path.is_file() and not (path.parent == root and path.name in {"README.md", "index.md"})
    )
