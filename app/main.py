from fastapi import FastAPI

from .routers.router import api_router
from .pkg.db import init_sessionmakers
from .pkg.settings import settings

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Initialize DB session factories from env at startup
init_sessionmakers()

app.include_router(api_router)