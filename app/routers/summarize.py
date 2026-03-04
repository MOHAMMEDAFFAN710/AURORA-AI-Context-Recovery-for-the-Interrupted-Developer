from fastapi import APIRouter
from app.schemas import AnalyzeRequest, AnalysisResult
from app.services.code_scanner import scan_project
from app.services.ai_summarizer import generate_explanations

router = APIRouter(prefix="/api", tags=["summarize"])

@router.post("/summarize", response_model=AnalysisResult)
async def summarize_project(req: AnalyzeRequest) -> AnalysisResult:
    files_scanned, todos, file_samples = scan_project(req.project_path, max_files=10) # Limit files for faster summary
    
    project_summary, _, file_summaries = await generate_explanations(file_samples, todos, {})

    return AnalysisResult(
        project_path=req.project_path,
        files_scanned=files_scanned,
        todos=todos,
        git_recent=[],
        project_explanation=project_summary,
        developer_briefing="",
        files_insights=file_summaries
    )
