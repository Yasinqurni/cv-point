from pydantic import BaseModel, Field
from typing import Optional


class MigrationAerisQuery(BaseModel):
    email: Optional[str] = Field(None, description="Filter users by email (optional)")
    limit: int = Field(100, ge=1, le=10000, description="Max number of records to process")
