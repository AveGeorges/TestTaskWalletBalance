from fastapi import FastAPI

from app.api.v1.wallets import router as wallets_router

app = FastAPI(title="Wallet API")

app.include_router(wallets_router, prefix="/api/v1/wallets", tags=["wallets"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
