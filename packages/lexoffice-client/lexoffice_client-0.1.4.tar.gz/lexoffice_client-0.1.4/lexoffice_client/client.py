import html
from pathlib import Path
from typing import Optional, List, Dict, Union
from uuid import UUID
import httpx
from lexoffice_client.common import CreateResponse
from lexoffice_client.contact import Contact, ContactWritable
from lexoffice_client.posting_category import PostingCategoryReadOnly
from lexoffice_client.voucher import Voucher, VoucherWritable
from lexoffice_client.file import File, Type

from urllib.parse import urlencode


class LexofficeClient:
    def __init__(
        self, access_token: str, base_url: str = "https://api.lexoffice.io/v1"
    ):
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
            base_url=base_url,
            timeout=10,
        )

    def ping(self):
        """Ping Lexoffice API and test the connection."""
        response = self.client.get("/ping")
        if not response.is_success:
            raise httpx.HTTPStatusError(
                f"Error pinging Lexoffice API: {response.status_code} - {response.text}",
                request=response.request,
                response=response,
            )

    def create_contact(self, contact: ContactWritable) -> CreateResponse:
        """Create a new contact.

        :param contact: The contact to create.
        :return: The response from the Lexoffice API.
        """

        response = self.client.post(
            "/contacts", json=contact.model_dump(exclude_none=True)
        )

        if not response.is_success:
            raise httpx.HTTPStatusError(
                f"Error creating contact: {response.status_code} - {response.text}",
                request=response.request,
                response=response,
            )

        return CreateResponse.model_validate(response.json())

    def retrieve_contact(self, contact_id: UUID) -> Contact:
        """Retrieve a contact by its ID.

        :param contact_id: The ID of the contact to retrieve.
        :return: The retrieved contact as a Contact object.
        """
        response = self.client.get(f"/contacts/{contact_id}")

        if not response.is_success:
            raise httpx.HTTPStatusError(
                f"Error retrieving contact: {response.status_code} - {response.text}",
                request=response.request,
                response=response,
            )

        return Contact.model_validate(response.json())

    def filter_contacts(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        number: Optional[int] = None,
        customer: Optional[bool] = None,
        vendor: Optional[bool] = None,
    ) -> List[Contact]:
        """Filter contacts by optional email, name, number, customer, and vendor.

        :param email: The email address to filter by (optional).
        :param name: The name to filter by (optional).
        :param number: The number of contacts to retrieve (optional).
        :param customer: Whether to filter by customer (optional).
        :param vendor: Whether to filter by vendor (optional).
        :return: A list of filtered contacts.
        """
        query_params: Dict[str, Union[str, None]] = {
            "email": html.escape(email) if email else None,
            "name": html.escape(name) if name else None,
            "number": str(number) if number is not None else None,
            "customer": str(customer).lower() if customer is not None else None,
            "vendor": str(vendor).lower() if vendor is not None else None,
        }
        query_params = {k: v for k, v in query_params.items() if v is not None}

        encoded_query = urlencode(query_params)
        response = self.client.get(f"/contacts?{encoded_query}")

        if not response.is_success:
            raise httpx.HTTPStatusError(
                f"Error filtering contacts: {response.status_code} - {response.text}",
                request=response.request,
                response=response,
            )

        content = response.json().get("content")
        if content is None:
            raise ValueError("Invalid response format: 'content' key not found.")
        return [Contact.model_validate(contact) for contact in content]

    def retrieve_posting_categories_list(self) -> List[PostingCategoryReadOnly]:
        """Retrieve a list of posting categories.

        :return: A list of PostingCategoryReadOnly objects.
        """
        response = self.client.get("/posting-categories")

        if not response.is_success:
            raise httpx.HTTPStatusError(
                f"Error retrieving posting categories: {response.status_code} - {response.text}",
                request=response.request,
                response=response,
            )

        content = response.json()
        if content is None:
            raise ValueError("Invalid response format: 'content' key not found.")
        return [
            PostingCategoryReadOnly.model_validate(category) for category in content
        ]

    def create_voucher(self, voucher: VoucherWritable) -> CreateResponse:
        """Create a new voucher.

        :param voucher: The voucher to create.
        :return: The response from the Lexoffice API.
        """
        response = self.client.post(
            "/vouchers", json=voucher.model_dump(exclude_none=True, mode="json")
        )

        if not response.is_success:
            raise httpx.HTTPStatusError(
                f"Error creating voucher: {response.status_code} - {response.text}",
                request=response.request,
                response=response,
            )

        return CreateResponse.model_validate(response.json())

    def retrieve_voucher(self, voucher_id: UUID) -> Voucher:
        """Retrieve a voucher by its ID.

        :param voucher_id: The ID of the voucher to retrieve.
        :return: The retrieved voucher as an Invoice object.
        """
        response = self.client.get(f"/vouchers/{voucher_id}")

        if not response.is_success:
            raise httpx.HTTPStatusError(
                f"Error retrieving voucher: {response.status_code} - {response.text}",
                request=response.request,
                response=response,
            )

        return Voucher.model_validate(response.json())

    def upload_file_to_voucher(
        self,
        voucher_id: UUID,
        file_path: Union[str, Path],
        upload_type: Type = Type.VOUCHER,
    ) -> File:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if file_path.stat().st_size > 5 * 1024 * 1024:
            raise ValueError("File size exceeds the 5MB limit.")

        files = {"file": open(file_path, "rb")}
        data = {"type": upload_type.value}

        response = self.client.post(
            f"/vouchers/{voucher_id}/files",
            files=files,
            data=data,
        )

        if not response.is_success:
            raise httpx.HTTPStatusError(
                f"Error uploading file: {response.status_code} - {response.text}",
                request=response.request,
                response=response,
            )

        return File.model_validate(response.json())
