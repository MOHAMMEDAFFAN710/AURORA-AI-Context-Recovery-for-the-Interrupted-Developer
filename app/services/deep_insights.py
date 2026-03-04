import os
import json
from typing import Any, Dict, List, Tuple

def _file_type(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return ext.replace(".", "") or "unknown"

def _role_from_path(path: str) -> str:
    p = path.replace("\\", "/").lower()
    if "/app/" in p or p.endswith(".py"):
        return "backend"
    if "aurora-frontend" in p or any(seg in p for seg in ["/src/", "next.config", "tailwind", ".tsx", ".jsx"]):
        return "frontend"
    if any(seg in p for seg in ["package.json", "requirements.txt", "pyproject.toml", "dockerfile", "compose.yml", ".env"]):
        return "configuration"
    return "code"

def summarize_file_content(content: str) -> str:
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    head = "\n".join(lines[:6])
    if len(head) > 600:
        head = head[:597] + "..."
    return head or "Source file"

def extract_file_insights(file_samples: Dict[str, str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for path, content in file_samples.items():
        lines = content.count("\n") + 1 if content else 0
        out.append({
            "path": path,
            "file_type": _file_type(path),
            "lines": lines,
            "role": _role_from_path(path),
            "summary": summarize_file_content(content),
        })
    return out

def build_folder_tree(root: str, max_depth: int = 3) -> Dict[str, Any]:
    def node_for(path: str, depth: int) -> Dict[str, Any]:
        name = os.path.basename(path) or path
        if os.path.isdir(path):
            if depth >= max_depth:
                return {"name": name, "path": path, "type": "dir", "children": []}
            children = []
            try:
                for entry in sorted(os.listdir(path))[:50]:
                    p = os.path.join(path, entry)
                    if entry.startswith(".") or entry in {"node_modules", ".venv", "__pycache__", ".next"}:
                        continue
                    children.append(node_for(p, depth + 1))
            except Exception:
                pass
            return {"name": name, "path": path, "type": "dir", "children": children}
        else:
            return {"name": name, "path": path, "type": "file", "file_type": _file_type(path), "role": _role_from_path(path)}
    return node_for(root, 0)

def detect_tech_stack(root: str, file_samples: Dict[str, str]) -> Tuple[List[str], List[Dict[str, str]]]:
    tech: List[str] = []
    files = set(file_samples.keys())
    names = {os.path.basename(p).lower(): p for p in files}
    content_join = "\n".join(file_samples.values()).lower()
    if "fastapi" in content_join:
        tech.append("FastAPI")
    if "pymongo" in content_join or "mongodb" in content_join:
        tech.append("MongoDB")
    if "next.config" in "".join(names.keys()) or ".tsx" in "".join(names.keys()):
        tech.append("Next.js")
    if "tailwind" in content_join or "tailwind.config" in "".join(names.keys()):
        tech.append("TailwindCSS")
    if "huggingface" in content_join:
        tech.append("HuggingFace")
    if "gitpython" in content_join:
        tech.append("GitPython")
    if "requirements.txt" in names:
        tech.append("Python")
    if "package.json" in names:
        tech.append("Node.js")
    links = []
    link_map = {
        "FastAPI": "https://fastapi.tiangolo.com/",
        "MongoDB": "https://www.mongodb.com/docs/",
        "Next.js": "https://nextjs.org/docs",
        "TailwindCSS": "https://tailwindcss.com/docs",
        "HuggingFace": "https://huggingface.co/docs",
        "GitPython": "https://gitpython.readthedocs.io/",
        "Python": "https://docs.python.org/3/",
        "Node.js": "https://nodejs.org/en/docs",
    }
    for t in tech:
        links.append({"name": t, "url": link_map.get(t, "")})
    return sorted(list(dict.fromkeys(tech))), links

def recent_activity_from_git(git_summary: Dict[str, Any]) -> Dict[str, Any]:
    commits = git_summary.get("commits", [])
    if not commits:
        return {"last_commit": None, "files_recent": []}
    last = commits[0]
    files_recent = last.get("files_changed", [])
    return {"last_commit": last, "files_recent": files_recent}
