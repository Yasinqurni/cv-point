from pydantic import BaseModel
from typing import Dict, Any

class MigrationAerisResponse(BaseModel):
    status: str
    result: Dict[str, Any]
