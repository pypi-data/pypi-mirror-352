from enum import Enum
from uuid import UUID
from pydantic import BaseModel


class Type(str, Enum):
    INCOME = "income"
    OUTGO = "outgo"


class PostingCategoryReadOnly(BaseModel):
    id: UUID
    name: str
    type: Type
    contactRequired: bool
    splitAllowed: bool
    groupName: str
