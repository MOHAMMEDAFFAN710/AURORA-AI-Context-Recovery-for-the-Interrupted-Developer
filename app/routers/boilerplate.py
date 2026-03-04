from fastapi import APIRouter
from app.schemas import BoilerplateRequest, BoilerplateResponse
from app.services.boilerplate_generator import generate

router = APIRouter(prefix="/api/boilerplate", tags=["boilerplate"])


@router.post("", response_model=BoilerplateResponse)
async def create_boilerplate(req: BoilerplateRequest) -> BoilerplateResponse:
    result = generate(req.kind, req.name, req.language)
    return BoilerplateResponse(name=result["name"], language=result["language"], content=result["content"])
/