"""FastAPI 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.claw import router as claw_router
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

    return app


app = create_app()


def get_port() -> int:
    return config.get("server.port", 18000)
