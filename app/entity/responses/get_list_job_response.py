

from pydantic import BaseModel

class GetListJobResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    requirements: str | None = None