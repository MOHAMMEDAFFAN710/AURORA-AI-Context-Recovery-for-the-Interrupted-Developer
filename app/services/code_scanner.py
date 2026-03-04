import os
import re
from typing import Dict, Iterable, List, Tuple
from app.config import settings


IGNORE_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".next", "target"}
TODO_PATTERN = re.compile(r"\b(TODO|FIXME|BUG)\b[:\- ]?(.*)", re.IGNORECASE)


def iter_source_files(root: str, max_files: int | None = None) -> Iterable[str]:
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for fname in filenames:
            if fname.lower().endswith(settings.scan_extensions):
                yield os.path.join(dirpath, fname)
                count += 1
                if max_files is not None and count >= max_files:
                    return


def read_file_sample(path: str, max_bytes: int) -> str:
    try:
        with open(path, "rb") as f:
            data = f.read(max_bytes)
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def detect_todos(path: str, content: str) -> List[Dict[str, str | int]]:
    out: List[Dict[str, str | int]] = []
    for idx, line in enumerate(content.splitlines(), start=1):
        m = TODO_PATTERN.search(line)
        if m:
            out.append(
                {
                    "file_path": path,
                    "line": idx,
                    "kind": m.group(1).upper(),
                    "text": m.group(2).strip(),
                }
            )
    return out


def scan_project(root: str, max_files: int | None = None) -> Tuple[int, List[Dict[str, str | int]], Dict[str, str]]:
    files = list(iter_source_files(root, max_files=max_files))
    todos: List[Dict[str, str | int]] = []
    file_samples: Dict[str, str] = {}
    for path in files:
        content = read_file_sample(path, settings.max_file_bytes)
        if content:
            file_samples[path] = content[: settings.max_file_bytes]
            todos.extend(detect_todos(path, content))
    return len(files), todos, file_samples
