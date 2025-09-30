from pydantic import BaseModel

class ResultCandidate(BaseModel):
    cv_match_rate: float
    cv_feedback: str
    project_score: float
    project_feedback: str
    overall_summary: str

class ResultCandidateResponse(BaseModel):
    id: int
    candidate_name: str | None
    job_name: str | None
    status: str
    result: ResultCandidate | None
