from datetime import datetime
from typing import Any, Dict, List, Optional


def new_session_document(
    project_path: str,
    files_scanned: int,
    todos: List[Dict[str, Any]],
    git_summary: Dict[str, Any],
    explanations: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "project_path": project_path,
        "files_scanned": files_scanned,
        "todos": todos,
        "git_summary": git_summary,
        "explanations": explanations,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


def to_public_session(doc: Dict[str, Any]) -> Dict[str, Any]:
    doc_out = dict(doc)
    if "_id" in doc_out:
        doc_out["id"] = str(doc_out.pop("_id"))
    return doc_out
