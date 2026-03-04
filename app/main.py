import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.logging_config import configure_logging
from app.routers.analysis import router as analysis_router
from app.routers.boilerplate import router as boilerplate_router


configure_logging()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)
app.include_router(boilerplate_router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.environment}
