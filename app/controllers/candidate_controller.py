from abc import ABC, abstractmethod
from fastapi import UploadFile, Depends
from app.services.candidate_service import CandidateService, CandidateServiceImpl, get_candidate_service
from app.pkg.interceptor.response import success_response, error_response

class CandidateController(ABC):
    @abstractmethod
    async def upload_candidate(self, candidate_name: str, job_id: int, cv: UploadFile, project_report: UploadFile):
        ...

    @abstractmethod
    async def evaluate_candidate(self, id: int):
        ...

    @abstractmethod
    async def get_result(self, id: int):
        ...

class CandidateControllerImpl(CandidateController):
    def __init__(self, service: CandidateService):
        self.service = service

    async def upload_candidate(self, candidate_name: str, job_id: int, cv: UploadFile, project_report: UploadFile):
        try:
            result = await self.service.handle_upload(candidate_name, job_id, cv, project_report)
            return success_response(result)
        except ValueError as ve:
            return error_response(message=str(ve), status_code=400)

    async def evaluate_candidate(self, id: int):
        try:
            result = await self.service.evaluate(id)
            return success_response(result)
        except ValueError as ve:
            return error_response(message=str(ve), status_code=400)

    async def get_result(self, id: int):
        try:
            result = await self.service.result(id)
            return success_response(result)
        except ValueError as ve:
            return error_response(message=str(ve), status_code=400)

def get_candidate_controller(
    service: CandidateServiceImpl = Depends(get_candidate_service),
) -> CandidateController:
    return CandidateControllerImpl(service)