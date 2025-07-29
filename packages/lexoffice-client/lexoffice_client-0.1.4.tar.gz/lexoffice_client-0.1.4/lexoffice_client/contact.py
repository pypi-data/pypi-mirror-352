from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, model_validator


class CountryCode(str, Enum):
    DE = "DE"


class Address(BaseModel):
    suppliment: Optional[str] = None
    street: Optional[str] = None
    zip: Optional[str] = None
    city: Optional[str] = None
    countryCode: CountryCode


class Addresses(BaseModel):
    billing: Optional[List[Address]] = None
    shipping: Optional[List[Address]] = None


class CompanyContactPerson(BaseModel):
    salutation: Optional[str] = None
    firstName: Optional[str] = None
    lastName: str
    emailAddress: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None


class Company(BaseModel):
    allowTaxFreeInvoices: Optional[bool] = None
    name: str
    taxNumber: Optional[str] = None
    vatRegistrationId: Optional[str] = None
    contactPersons: Optional[List[CompanyContactPerson]] = None


class Person(BaseModel):
    salutation: Optional[str] = None
    firstName: Optional[str] = None
    lastName: str


class Role(BaseModel):
    number: Optional[int] = None


class Roles(BaseModel):
    customer: Optional[Role] = None
    vendor: Optional[Role] = None

    @model_validator(mode="after")
    def check_model(self) -> "Roles":
        if bool(self.customer) == bool(self.vendor):
            raise ValueError("Exactly one of 'customer' or 'vendor' must be set.")
        return self


class ContactReadOnly(BaseModel):
    id: UUID
    organizationId: UUID
    archived: bool


class ContactWritable(BaseModel):
    roles: Roles
    company: Optional[Company] = None
    person: Optional[Person] = None
    addresses: Optional[Addresses] = None

    @model_validator(mode="after")
    def check_model(self) -> "ContactWritable":
        if bool(self.company) == bool(self.person):
            raise ValueError("Exactly one of 'company' or 'person' must be set.")
        return self


class Contact(ContactReadOnly, ContactWritable):
    pass
