from fastapi import APIRouter

from .migration_user_aeris_router import router as aeris_router

api_router = APIRouter()

@api_router.get("/health")
async def health() -> dict:
    return {"status": "ok"}

api_router.include_router(aeris_router, prefix="/api")
