from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class ErrorInterceptor(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Log error
            logger.error("Unhandled error", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": str(exc) or "Internal Server Error",
                    "data": None,
                },
            )
