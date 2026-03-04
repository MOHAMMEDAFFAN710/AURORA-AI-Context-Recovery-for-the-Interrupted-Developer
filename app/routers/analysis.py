from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List
import os
from app.schemas import AnalyzeRequest, AnalysisResult, GitCommitSummary, TodoItem
from app.services.code_scanner import scan_project
from app.services.git_analyzer import summarize_recent_commits
from app.services.ai_summarizer import generate_explanations
from app.db.mongo import get_db
from app.models.session import new_session_document, to_public_session
from bson import ObjectId
from pymongo.errors import PyMongoError

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResult)
async def analyze(req: AnalyzeRequest) -> AnalysisResult:
    path = os.path.abspath(req.project_path)
    if not os.path.exists(path):
        raise HTTPException(status_code=400, detail="project_path does not exist")
    files_scanned, todos_raw, file_samples = scan_project(path, max_files=req.max_files)
    git_summary = summarize_recent_commits(path, limit=10)
    project_explanation, developer_briefing = await generate_explanations(file_samples, todos_raw, git_summary)
    try:
        db = get_db()
        doc = new_session_document(
            project_path=path,
            files_scanned=files_scanned,
            todos=todos_raw,
            git_summary=git_summary,
            explanations={"project_explanation": project_explanation, "developer_briefing": developer_briefing},
        )
        await db.sessions.insert_one(doc)
    except Exception:
        pass
    todos = [TodoItem(**{k: v for k, v in t.items() if k in {"file_path", "line", "kind", "text"}}) for t in todos_raw]
    commits = [
        GitCommitSummary(
            commit=c["commit"],
            author=c["author"],
            date=c["date"],
            message=c["message"],
            files_changed=c.get("files_changed", []),
        )
        for c in git_summary.get("commits", [])
    ]
    return AnalysisResult(
        project_path=path,
        files_scanned=files_scanned,
        todos=todos,
        git_recent=commits,
        project_explanation=project_explanation,
        developer_briefing=developer_briefing,
    )


@router.get("/sessions")
async def list_sessions() -> List[Dict[str, Any]]:
    try:
        db = get_db()
        out: List[Dict[str, Any]] = []
        async for doc in db.sessions.find().sort("created_at", -1).limit(50):
            out.append(to_public_session(doc))
        return out
    except Exception:
        return []


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    try:
        db = get_db()
        try:
            oid = ObjectId(session_id)
        except Exception:
            raise HTTPException(status_code=400, detail="invalid session id")
        doc = await db.sessions.find_one({"_id": oid})
        if not doc:
            raise HTTPException(status_code=404, detail="session not found")
        return to_public_session(doc)
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")
