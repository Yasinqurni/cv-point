from fastapi import Form, UploadFile, File
from pydantic import BaseModel

class CandidateMeta(BaseModel):
    candidate_name: str
    job_id: int

    @classmethod
    def as_form(
        cls,
        candidate_name: str = Form(...),
        job_id: int = Form(...),
    ):
        return cls(candidate_name=candidate_name, job_id=job_id)
