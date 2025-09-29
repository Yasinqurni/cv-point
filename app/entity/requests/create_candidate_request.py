from pydantic import BaseModel
from fastapi import UploadFile

class CreateCandidateRequest(BaseModel):
    cv: UploadFile
    project_report: UploadFile
    candidate_name: str
    job_id: int