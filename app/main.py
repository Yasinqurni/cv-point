from fastapi import FastAPI
from contextlib import asynccontextmanager

from .pkg.config import get_config
from .pkg.db import engine
from .pkg.interceptor.interceptor import ErrorInterceptor
from .pkg.interceptor.exception import register_exception_handlers
from .di import get_job_router
from .routers.job_router import JobRouter
from sqlalchemy import text
from .pkg.rabbitmq import get_channel

config = get_config()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connected")
    except Exception as e:
        print("Database connection failed:", e)
        raise

    # RabbitMQ
    try:
        app.state.rabbitmq_channel = await get_channel()
        print("RabbitMQ channel ready")
    except Exception as e:
        print("RabbitMQ connection failed:", e)
        raise


    # Register router
    job_router: JobRouter = get_job_router()
    app.include_router(job_router.get_router(), prefix="/api/v1")

    yield

    # Shutdown (cleanup)
    engine.dispose()
    print("Database engine disposed")




app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    lifespan=lifespan,
)

# Middleware & Exception
app.add_middleware(ErrorInterceptor)
register_exception_handlers(app)
