from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse

class NotFoundError(Exception):
    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(message)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": exc.message,
                "errors": None,
            },
        )
