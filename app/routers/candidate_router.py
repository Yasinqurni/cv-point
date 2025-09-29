from fastapi import APIRouter, Depends
from app.controllers.candidate_controller import CandidateControllerImpl, get_candidate_controller
from app.entity.requests.create_candidate_request import CreateCandidateRequest

class CandidateRouter:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.post("/candidates/upload")
        async def upload_candidate(req: CreateCandidateRequest, controller: CandidateControllerImpl = Depends(get_candidate_controller)):
            return await controller.upload_candidate(req)

        @self.router.post("/candidates/{id}/evaluate")
        async def evaluate_candidate(id: int, controller: CandidateControllerImpl = Depends(get_candidate_controller)):
            return await controller.evaluate_candidate(id)

        @self.router.get("/candidates/{id}/result")
        async def get_result(id: int, controller: CandidateControllerImpl = Depends(get_candidate_controller)):
            return await controller.get_result(id)

    def get_router(self) -> APIRouter:
        return self.router