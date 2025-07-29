from enum import Enum
from pydantic import BaseModel, EmailStr as EmailStr
from uuid import UUID

class CountryCode(str, Enum):
    DE = "DE"

class Address(BaseModel):
    suppliment: str | None
    street: str | None
    zip: str | None
    city: str | None
    countryCode: CountryCode

class Addresses(BaseModel):
    billing: Address | None
    shipping: Address | None

class CompanyContactPerson(BaseModel):
    salutation: str | None
    firstName: str | None
    lastName: str
    emailAddress: EmailStr | None
    phoneNumber: str | None

class Company(BaseModel):
    allowTaxFreeInvoices: bool | None
    name: str
    taxNumber: str | None
    vatRegistrationId: str | None
    contactPersons: list[CompanyContactPerson] | None

class Person(BaseModel):
    salutation: str | None
    firstName: str | None
    lastName: str

class Role(BaseModel):
    number: int | None

class Roles(BaseModel):
    customer: Role | None
    vendor: Role | None
    def check_model(self) -> Roles: ...

class ContactReadOnly(BaseModel):
    id: UUID
    organizationId: UUID
    archived: bool

class ContactWritable(BaseModel):
    roles: Roles
    company: Company | None
    person: Person | None
    addresses: str | None
    def check_model(self) -> ContactWritable: ...

class Contact(ContactReadOnly, ContactWritable): ...
