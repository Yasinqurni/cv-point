

from pydantic import BaseModel

class GetListJobResponse(BaseModel):
    id: int
    title: str