from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.middleware import RequestIdMiddleware
from app.api.v1.wallets import router as wallets_router
from app.core.telemetry import setup_telemetry
from app.db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(title="Wallet API")

    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)
    app.include_router(wallets_router, prefix="/api/v1/wallets", tags=["wallets"])

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    setup_telemetry(app, engine=engine)
    return app


app = create_app()
