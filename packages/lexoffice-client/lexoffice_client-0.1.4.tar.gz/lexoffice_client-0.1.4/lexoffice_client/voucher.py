from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, model_validator


class VoucherType(str, Enum):
    SALES_INVOICE = "salesinvoice"
    SALES_CREDIT_NOTE = "salescreditnote"
    PURCHASE_INVOICE = "purchaseinvoice"
    PURCHASE_CREDIT_NOTE = "purchasecreditnote"


class VoucherStatus(str, Enum):
    UNCHECKED = "unchecked"
    OPEN = "open"


class TaxType(str, Enum):
    NET = "net"
    GROSS = "gross"


class VoucherItem(BaseModel):
    amount: float
    taxAmount: float
    taxRatePercent: float
    categoryId: UUID


class VoucherReadOnly(BaseModel):
    id: UUID
    organizationId: UUID
    createdDate: datetime
    updatedDate: datetime


class VoucherWritable(BaseModel):
    type: VoucherType
    voucherStatus: Optional[VoucherStatus] = None
    voucherNumber: Optional[str] = None
    voucherDate: Optional[datetime] = None
    shippingDate: Optional[datetime] = None
    dueDate: Optional[datetime] = None
    totalGrossAmount: float
    totalTaxAmount: float
    taxType: TaxType
    useCollectiveContact: Optional[bool] = None
    contactId: Optional[UUID] = None
    remark: Optional[str] = None
    voucherItems: List[VoucherItem]
    version: Optional[int] = None
    files: Optional[List[str]] = None

    @model_validator(mode="after")
    def check_model(self) -> "VoucherWritable":
        if self.voucherStatus != VoucherStatus.UNCHECKED:
            if (
                not self.voucherNumber
                or not self.voucherDate
                or not self.totalGrossAmount
                or not self.totalTaxAmount
            ):
                raise ValueError(
                    "voucherNumber, voucherDate, totalGrossAmount and totalTaxAmount are required when voucherStatus is not unchecked."
                )
        if not self.useCollectiveContact:
            if not self.contactId:
                raise ValueError(
                    "contactId is required when useCollectiveContact is false."
                )
        return self


class Voucher(VoucherReadOnly, VoucherWritable):
    pass
