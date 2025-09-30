from .routers.job_router import JobRouter, JobRouterImpl
from .routers.candidate_router import CandidateRouter, CandidateRouterImpl

def get_job_router() -> JobRouter:
    return JobRouterImpl()

def get_candidate_router() -> CandidateRouter:
    return CandidateRouterImpl()
