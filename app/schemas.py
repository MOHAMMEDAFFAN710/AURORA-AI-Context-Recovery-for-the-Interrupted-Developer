from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class AnalyzeRequest(BaseModel):
    project_path: str = Field(..., min_length=1)
    max_files: Optional[int] = None


class TodoItem(BaseModel):
    file_path: str
    line: int
    kind: str
    text: str


class GitCommitSummary(BaseModel):
    commit: str
    author: str
    date: str
    message: str
    files_changed: List[str] = []


class AnalysisResult(BaseModel):
    project_path: str
    files_scanned: int
    todos: List[TodoItem]
    git_recent: List[GitCommitSummary]
    project_explanation: str
    developer_briefing: str


class SessionRecord(BaseModel):
    id: str
    project_path: str
    files_scanned: int
    todos: List[TodoItem]
    git_summary: Dict[str, Any]
    explanations: Dict[str, Any]
    created_at: str
    updated_at: str


class BoilerplateRequest(BaseModel):
    kind: str
    name: Optional[str] = None
    language: Optional[str] = None


class BoilerplateResponse(BaseModel):
    name: str
    language: str
    content: str
