from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class CreateResponse(BaseModel):
    id: UUID
    resourceUri: str
    createdDate: datetime
    updatedDate: datetime
    version: int
