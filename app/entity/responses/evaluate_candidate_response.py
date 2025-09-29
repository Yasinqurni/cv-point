from pydantic import BaseModel

class EvaluateCandidateResponse(BaseModel):
    id: int
    status: str
