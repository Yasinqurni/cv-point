from abc import ABC, abstractmethod
from fastapi import UploadFile
from app.services.job_service import JobService, JobServiceImpl, get_job_service
from fastapi import Depends
from app.pkg.interceptor.response import success_response, error_response


class JobController(ABC):
    @abstractmethod
    async def upload_job(self, file: UploadFile):
        pass


class JobControllerImpl(JobController):
    def __init__(self, service: JobService):
        self.service = service

    async def upload_job(self, file: UploadFile):
        try:
            result = await self.service.handle_upload(file)
            return success_response(result)
        except ValueError as ve:
            return error_response(message=str(ve), status_code=400)



def get_job_controller(
    service: JobServiceImpl = Depends(get_job_service),
) -> JobController:
    return JobControllerImpl(service)