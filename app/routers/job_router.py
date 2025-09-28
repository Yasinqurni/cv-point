from fastapi import APIRouter, UploadFile, Depends
from ..controllers.job_controller import JobControllerImpl, get_job_controller
from abc import ABC, abstractmethod
from fastapi import APIRouter

class JobRouter(ABC):
    @abstractmethod
    def get_router(self) -> APIRouter:
        ...

class JobRouterImpl(JobRouter):
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.post("/jobs/upload")
        async def upload_job(file: UploadFile, controller: JobControllerImpl = Depends(get_job_controller)):
            return await controller.upload_job(file)
        
        @self.router.get("/jobs")
        async def get_list(controller: JobControllerImpl = Depends(get_job_controller)):
            return await controller.get_list()

    def get_router(self) -> APIRouter:
        return self.router
