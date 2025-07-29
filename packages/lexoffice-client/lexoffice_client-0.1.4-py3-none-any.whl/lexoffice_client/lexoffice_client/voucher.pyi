from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from uuid import UUID

class VoucherType(str, Enum):
    SALES_INVOICE = 'salesinvoice'
    SALES_CREDIT_NOTE = 'salesCreditNote'
    PURCHASE_INVOICE = 'purchaseInvoice'
    PURCAHSE_CREDIT_NOTE = 'purchaseCreditNote'

class VoucherStatus(str, Enum):
    UNCHECKED = 'unchecked'
    OPEN = 'open'

class TaxType(str, Enum):
    NET = 'net'
    GROSS = 'gross'

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
    voucherStatus: VoucherStatus | None
    voucherNumber: str | None
    voucherDate: datetime | None
    shippingDate: datetime | None
    dueDate: datetime | None
    totalGrossAmount: float
    totalTaxAmount: float
    taxType: TaxType
    useCollectiveContact: bool | None
    contactId: UUID | None
    remark: str | None
    voucherItems: list[VoucherItem]
    version: int | None
    files: list[str] | None
    def check_model(self) -> VoucherWritable: ...

class Voucher(VoucherReadOnly, VoucherWritable): ...
