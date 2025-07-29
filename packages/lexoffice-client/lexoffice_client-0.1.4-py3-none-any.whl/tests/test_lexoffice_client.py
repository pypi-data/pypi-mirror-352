from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from lexoffice_client.client import CreateResponse, LexofficeClient
from lexoffice_client.contact import Contact, ContactWritable, Person, Role, Roles
from lexoffice_client.voucher import (
    TaxType,
    Voucher,
    VoucherItem,
    VoucherStatus,
    VoucherType,
    VoucherWritable,
)

ORGANIZATION_ID = uuid4()
CONTACT_ID = uuid4()
VOUCHER_ID = uuid4()
CATEGORY_ID = uuid4()

NOW = datetime.now()


class TestLexofficeClient(unittest.TestCase):
    def setUp(self):
        self.access_token = "test_token"
        self.client = LexofficeClient(access_token=self.access_token)

    @patch("httpx.Client.get")
    def test_ping(self, mock_get: MagicMock):
        mock_get.return_value = MagicMock(status_code=200)
        self.client.ping()
        mock_get.assert_called_once_with("/ping")

    @patch("httpx.Client.post")
    def test_create_contact(self, mock_post: MagicMock):
        contact = ContactWritable(
            roles=Roles(customer=Role()), person=Person(lastName="Test")
        )
        mock_response = MagicMock(status_code=201)
        mock_response.json.return_value = CreateResponse(
            id=CONTACT_ID,
            resourceUri=f"/contacts/{CONTACT_ID}",
            createdDate=NOW,
            updatedDate=NOW,
            version=1,
        )
        mock_post.return_value = mock_response

        result = self.client.create_contact(contact)
        mock_post.assert_called_once()
        self.assertEqual(result.id, CONTACT_ID)

    @patch("httpx.Client.get")
    def test_retrieve_contact(self, mock_get: MagicMock):
        mock_response = MagicMock(status_code=200)

        contact = Contact(
            id=CONTACT_ID,
            organizationId=ORGANIZATION_ID,
            roles=Roles(customer=Role()),
            person=Person(lastName="Test"),
            archived=False,
        )

        mock_response.json.return_value = contact.model_dump()
        mock_get.return_value = mock_response

        result = self.client.retrieve_contact(CONTACT_ID)
        mock_get.assert_called_once_with(f"/contacts/{CONTACT_ID}")
        self.assertEqual(result.id, CONTACT_ID)

    @patch("httpx.Client.get")
    def test_filter_contacts(self, mock_get: MagicMock):
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {"content": []}
        mock_get.return_value = mock_response

        result = self.client.filter_contacts(email="test@example.com")
        mock_get.assert_called_once()
        self.assertEqual(result, [])

    @patch("httpx.Client.post")
    def test_create_voucher(self, mock_post: MagicMock):
        voucher = VoucherWritable(
            type=VoucherType.SALES_INVOICE,
            voucherStatus=VoucherStatus.UNCHECKED,
            totalGrossAmount=119.0,
            totalTaxAmount=19.0,
            taxType=TaxType.GROSS,
            useCollectiveContact=True,
            voucherItems=[
                VoucherItem(
                    amount=100.0,
                    taxAmount=19.0,
                    taxRatePercent=19.0,
                    categoryId=CATEGORY_ID,
                )
            ],
        )
        mock_response = MagicMock(status_code=201)
        mock_response.json.return_value = CreateResponse(
            id=VOUCHER_ID,
            resourceUri=f"/vouchers/{VOUCHER_ID}",
            createdDate=NOW,
            updatedDate=NOW,
            version=1,
        )
        mock_post.return_value = mock_response

        result = self.client.create_voucher(voucher)
        mock_post.assert_called_once()
        self.assertEqual(result.id, VOUCHER_ID)

    @patch("httpx.Client.get")
    def test_retrieve_voucher(self, mock_get: MagicMock):
        mock_response = MagicMock(status_code=200)

        voucher = Voucher(
            id=VOUCHER_ID,
            organizationId=VOUCHER_ID,
            createdDate=NOW,
            updatedDate=NOW,
            type=VoucherType.SALES_INVOICE,
            voucherStatus=VoucherStatus.UNCHECKED,
            totalGrossAmount=119.0,
            totalTaxAmount=19.0,
            taxType=TaxType.GROSS,
            useCollectiveContact=True,
            voucherItems=[
                VoucherItem(
                    amount=100.0,
                    taxAmount=19.0,
                    taxRatePercent=19.0,
                    categoryId=uuid4(),
                )
            ],
        )

        mock_response.json.return_value = voucher.model_dump()
        mock_get.return_value = mock_response

        result = self.client.retrieve_voucher(VOUCHER_ID)
        mock_get.assert_called_once_with(f"/vouchers/{VOUCHER_ID}")
        self.assertEqual(result.id, VOUCHER_ID)


if __name__ == "__main__":
    unittest.main()
