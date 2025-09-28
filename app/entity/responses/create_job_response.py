from pydantic import BaseModel

class CreateJobResponse(BaseModel):
    id: int
    file_url: str
    status: str
