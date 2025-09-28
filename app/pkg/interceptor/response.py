from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from functools import wraps


def success_response(data=None, message: str = "OK"):
    return JSONResponse(
        content={
            "success": True,
            "message": message,
            "data": jsonable_encoder(data),
        }
    )


def error_response(message: str = "Error", errors=None, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "errors": jsonable_encoder(errors),
        },
    )
