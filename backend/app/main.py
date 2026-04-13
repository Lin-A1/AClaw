"""FastAPI 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.claw import router as claw_router
from app.api.memory import router as memory_router
from app.api.skills import router as skills_router
from app import config


def create_app() -> FastAPI:
    app = FastAPI(title="MultClaw API")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(claw_router, prefix="/api/claw", tags=["claw"])
    app.include_router(memory_router, prefix="/api/claw/memory", tags=["memory"])
    app.include_router(skills_router, prefix="/api/claw/skills", tags=["skills"])

    return app


app = create_app()


def get_port() -> int:
    return config.get("port", 18000)
