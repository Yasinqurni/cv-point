from .routers.job_router import JobRouter, JobRouterImpl
from .controllers.job_controller import JobControllerImpl, get_job_controller

def get_job_router() -> JobRouter:
    return JobRouterImpl()
