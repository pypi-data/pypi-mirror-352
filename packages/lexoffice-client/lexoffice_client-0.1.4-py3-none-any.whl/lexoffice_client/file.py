from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class Type(str, Enum):
    VOUCHER = "voucher"


class File(BaseModel):
    id: UUID
    voucherId: Optional[UUID] = None
