"""Tests for WFRMLS History module."""

from datetime import date, datetime
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from wfrmls.exceptions import WFRMLSError
from wfrmls.history import (
    HistoryStatus,
    HistoryTransactionalClient,
    HistoryTransactionType,
)


class TestHistoryTransactionType:
    """Test suite for HistoryTransactionType enum."""

    def test_history_transaction_type_values(self) -> None:
        """Test HistoryTransactionType enum values."""
        assert HistoryTransactionType.SALE.value == "Sale"
        assert HistoryTransactionType.LEASE.value == "Lease"
        assert HistoryTransactionType.RENTAL.value == "Rental"
        assert HistoryTransactionType.AUCTION.value == "Auction"


class TestHistoryStatus:
    """Test suite for HistoryStatus enum."""

    def test_history_status_values(self) -> None:
        """Test HistoryStatus enum values."""
        assert HistoryStatus.CLOSED.value == "Closed"
        assert HistoryStatus.SOLD.value == "Sold"
        assert HistoryStatus.LEASED.value == "Leased"
        assert HistoryStatus.EXPIRED.value == "Expired"
        assert HistoryStatus.WITHDRAWN.value == "Withdrawn"


class TestHistoryTransactionalClient:
    """Test suite for HistoryTransactionalClient class."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.client = HistoryTransactionalClient(bearer_token="test_token")

    @patch("wfrmls.history.HistoryTransactionalClient.get")
    def test_get_history_transactions_basic(self, mock_get: Mock) -> None:
        """Test basic get_history_transactions functionality."""
        mock_response: Dict[str, Any] = {
            "value": [
                {
                    "TransactionKey": "T123",
                    "ClosePrice": 500000,
                    "CloseDate": "2024-01-01T12:00:00Z",
                    "TransactionType": "Sale",
                }
            ]
        }
        mock_get.return_value = mock_response

        result = self.client.get_history_transactions()

        mock_get.assert_called_once_with("HistoryTransactional", params={})
        assert result == mock_response

    @patch("wfrmls.history.HistoryTransactionalClient.get")
    def test_get_history_transactions_with_all_params(self, mock_get: Mock) -> None:
        """Test get_history_transactions with all parameters."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get.return_value = mock_response

        result = self.client.get_history_transactions(
            top=50,
            skip=10,
            filter_query="TransactionType eq 'Sale'",
            select=["TransactionKey", "ClosePrice"],
            orderby="CloseDate desc",
            expand=["Property"],
            count=True,
        )

        expected_params = {
            "$top": 50,
            "$skip": 10,
            "$filter": "TransactionType eq 'Sale'",
            "$select": "TransactionKey,ClosePrice",
            "$orderby": "CloseDate desc",
            "$expand": "Property",
            "$count": "true",
        }

        mock_get.assert_called_once_with("HistoryTransactional", params=expected_params)

    @patch("wfrmls.history.HistoryTransactionalClient.get")
    def test_get_history_transactions_top_limit_enforcement(
        self, mock_get: Mock
    ) -> None:
        """Test that top parameter is limited to 200."""
        mock_get.return_value = {"value": []}

        self.client.get_history_transactions(top=300)

        expected_params = {"$top": 200}
        mock_get.assert_called_once_with("HistoryTransactional", params=expected_params)

    @patch("wfrmls.history.HistoryTransactionalClient.get")
    def test_get_history_transaction(self, mock_get: Mock) -> None:
        """Test get_history_transaction functionality."""
        transaction_key = "T123"
        mock_response: Dict[str, Any] = {
            "TransactionKey": transaction_key,
            "ClosePrice": 500000,
            "CloseDate": "2024-01-01T12:00:00Z",
        }
        mock_get.return_value = mock_response

        result = self.client.get_history_transaction(transaction_key)

        mock_get.assert_called_once_with(f"HistoryTransactional('{transaction_key}')")
        assert result == mock_response

    @patch("wfrmls.history.HistoryTransactionalClient.get_history_transactions")
    def test_get_transactions_for_property(self, mock_get_transactions: Mock) -> None:
        """Test get_transactions_for_property functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_transactions.return_value = mock_response

        result = self.client.get_transactions_for_property(
            listing_key="12345", orderby="CloseDate desc"
        )

        mock_get_transactions.assert_called_once_with(
            filter_query="ListingKey eq '12345'", orderby="CloseDate desc"
        )

    @patch("wfrmls.history.HistoryTransactionalClient.get_history_transactions")
    def test_get_sales_by_price_range(self, mock_get_transactions: Mock) -> None:
        """Test get_sales_by_price_range functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_transactions.return_value = mock_response

        result = self.client.get_sales_by_price_range(
            min_price=400000, max_price=600000, orderby="CloseDate desc"
        )

        expected_filter = "TransactionType eq 'Sale' and ClosePrice ge 400000 and ClosePrice le 600000"
        mock_get_transactions.assert_called_once_with(
            filter_query=expected_filter, orderby="CloseDate desc"
        )

    @patch("wfrmls.history.HistoryTransactionalClient.get_history_transactions")
    def test_get_recent_sales(self, mock_get_transactions: Mock) -> None:
        """Test get_recent_sales functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_transactions.return_value = mock_response

        result = self.client.get_recent_sales(days_back=30, orderby="CloseDate desc")

        # Check that the filter contains the expected parts
        mock_get_transactions.assert_called_once()
        call_args = mock_get_transactions.call_args
        assert "filter_query" in call_args.kwargs
        assert "TransactionType eq 'Sale'" in call_args.kwargs["filter_query"]
        assert "CloseDate ge" in call_args.kwargs["filter_query"]

    @patch("wfrmls.history.HistoryTransactionalClient.get_history_transactions")
    def test_get_transactions_by_city(self, mock_get_transactions: Mock) -> None:
        """Test get_transactions_by_city functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_transactions.return_value = mock_response

        result = self.client.get_transactions_by_city(
            city="Salt Lake City", orderby="CloseDate desc"
        )

        mock_get_transactions.assert_called_once_with(
            filter_query="City eq 'Salt Lake City'", orderby="CloseDate desc"
        )

    @patch("wfrmls.history.HistoryTransactionalClient.get_history_transactions")
    def test_get_closed_transactions(self, mock_get_transactions: Mock) -> None:
        """Test get_closed_transactions functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_transactions.return_value = mock_response

        result = self.client.get_closed_transactions(orderby="CloseDate desc")

        mock_get_transactions.assert_called_once_with(
            filter_query="Status eq 'Closed'", orderby="CloseDate desc"
        )

    @patch("wfrmls.history.HistoryTransactionalClient.get_history_transactions")
    def test_get_transactions_with_property(self, mock_get_transactions: Mock) -> None:
        """Test get_transactions_with_property functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_transactions.return_value = mock_response

        result = self.client.get_transactions_with_property(
            orderby="CloseDate desc", top=25
        )

        mock_get_transactions.assert_called_once_with(
            expand="Property", orderby="CloseDate desc", top=25
        )

    @patch("wfrmls.history.HistoryTransactionalClient.get_history_transactions")
    def test_get_modified_transactions_datetime(
        self, mock_get_transactions: Mock
    ) -> None:
        """Test get_modified_transactions with datetime object."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_transactions.return_value = mock_response

        since_datetime = datetime(2024, 1, 1, 12, 0, 0)
        result = self.client.get_modified_transactions(
            since=since_datetime, orderby="ModificationTimestamp desc"
        )

        expected_filter = "ModificationTimestamp gt '2024-01-01T12:00:00Z'"
        mock_get_transactions.assert_called_once_with(
            filter_query=expected_filter, orderby="ModificationTimestamp desc"
        )

    @patch("wfrmls.history.HistoryTransactionalClient.get_history_transactions")
    def test_get_sales_by_date_range(self, mock_get_transactions: Mock) -> None:
        """Test get_sales_by_date_range functionality."""
        mock_response: Dict[str, Any] = {"value": []}
        mock_get_transactions.return_value = mock_response

        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        result = self.client.get_sales_by_date_range(
            start_date=start_date, end_date=end_date, orderby="CloseDate desc"
        )

        expected_filter = "TransactionType eq 'Sale' and CloseDate ge '2024-01-01' and CloseDate le '2024-01-31'"
        mock_get_transactions.assert_called_once_with(
            filter_query=expected_filter, orderby="CloseDate desc"
        )

    def test_init_default_params(self) -> None:
        """Test HistoryTransactionalClient initialization with default parameters."""
        client = HistoryTransactionalClient()
        # Test that it doesn't raise an exception and creates properly
        assert hasattr(client, "bearer_token")
        assert hasattr(client, "base_url")

    def test_init_with_params(self) -> None:
        """Test HistoryTransactionalClient initialization with custom parameters."""
        client = HistoryTransactionalClient(
            bearer_token="custom_token", base_url="https://custom.api.com"
        )
        assert hasattr(client, "bearer_token")
        assert hasattr(client, "base_url")
