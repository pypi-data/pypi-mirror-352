from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

class CreateResponse(BaseModel):
    id: UUID
    resourceUri: str
    createdDate: datetime
    updatedDate: datetime
    version: int
