"""HistoryTransactional client for WFRMLS API."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .base_client import BaseClient


class HistoryTransactionType(Enum):
    """History transaction type options."""

    SALE = "Sale"
    LEASE = "Lease"
    RENTAL = "Rental"
    AUCTION = "Auction"


class HistoryStatus(Enum):
    """History status options."""

    CLOSED = "Closed"
    SOLD = "Sold"
    LEASED = "Leased"
    EXPIRED = "Expired"
    WITHDRAWN = "Withdrawn"


class HistoryTransactionalClient(BaseClient):
    """Client for historical transaction data API endpoints.

    The HistoryTransactional resource contains historical property transaction
    information including sale prices, dates, and other transaction details.
    This is valuable for market analysis, comparable sales, and pricing trends.
    """

    def __init__(
        self, bearer_token: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the history transactional client.

        Args:
            bearer_token: Bearer token for authentication
            base_url: Base URL for the API
        """
        super().__init__(bearer_token=bearer_token, base_url=base_url)

    def get_history_transactions(
        self,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        filter_query: Optional[str] = None,
        select: Optional[Union[List[str], str]] = None,
        orderby: Optional[str] = None,
        expand: Optional[Union[List[str], str]] = None,
        count: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Get historical transactions with optional OData filtering.

        This method retrieves historical transaction data with full OData v4.0 query support.
        Useful for market analysis, comparable sales research, and pricing trends.

        Args:
            top: Number of results to return (OData $top, max 200 per API limit)
            skip: Number of results to skip (OData $skip) - use with caution for large datasets
            filter_query: OData filter query string for complex filtering
            select: Fields to select (OData $select) - can be list or comma-separated string
            orderby: Order by clause (OData $orderby) for result sorting
            expand: Related resources to include (OData $expand) - can be list or comma-separated string
            count: Include total count in results (OData $count)

        Returns:
            Dictionary containing history transaction data with structure:
                - @odata.context: Metadata URL
                - @odata.count: Total count (if requested)
                - @odata.nextLink: Next page URL (if more results available)
                - value: List of transaction records

        Raises:
            WFRMLSError: If the API request fails
            ValidationError: If OData query parameters are invalid
            RateLimitError: If the rate limit is exceeded

        Example:
            ```python
            # Get recent sales transactions
            recent_sales = client.history.get_history_transactions(
                filter_query="TransactionType eq 'Sale' and CloseDate gt '2023-01-01'",
                orderby="CloseDate desc",
                top=50
            )

            # Get transactions with property info
            transactions = client.history.get_history_transactions(
                expand="Property",
                top=25
            )

            # Get specific transaction fields
            transactions = client.history.get_history_transactions(
                select=["ListingKey", "ClosePrice", "CloseDate", "TransactionType"],
                filter_query="ClosePrice gt 500000",
                orderby="ClosePrice desc"
            )
            ```
        """
        params: Dict[str, Any] = {}

        if top is not None:
            # Enforce 200 record limit as per API specification
            params["$top"] = min(top, 200)
        if skip is not None:
            params["$skip"] = skip
        if filter_query is not None:
            params["$filter"] = filter_query
        if orderby is not None:
            params["$orderby"] = orderby
        if count is not None:
            params["$count"] = "true" if count else "false"

        if select is not None:
            if isinstance(select, list):
                params["$select"] = ",".join(select)
            else:
                params["$select"] = select

        if expand is not None:
            if isinstance(expand, list):
                params["$expand"] = ",".join(expand)
            else:
                params["$expand"] = expand

        return self.get("HistoryTransactional", params=params)

    def get_history_transaction(self, transaction_key: str) -> Dict[str, Any]:
        """Get historical transaction by transaction key.

        Retrieves a single historical transaction record by its unique key.
        This is the most efficient way to get detailed information about
        a specific transaction.

        Args:
            transaction_key: Transaction key to retrieve (unique identifier)

        Returns:
            Dictionary containing transaction data for the specified record

        Raises:
            NotFoundError: If the transaction with the given key is not found
            WFRMLSError: If the API request fails

        Example:
            ```python
            # Get specific transaction by key
            transaction = client.history.get_history_transaction("TXN123456")

            print(f"Sale Price: ${transaction['ClosePrice']:,}")
            print(f"Close Date: {transaction['CloseDate']}")
            print(f"Property: {transaction['ListingKey']}")
            ```
        """
        return self.get(f"HistoryTransactional('{transaction_key}')")

    def get_transactions_for_property(
        self, listing_key: str, **kwargs: Any
    ) -> Dict[str, Any]:
        """Get historical transactions for a specific property.

        Convenience method to retrieve all historical transactions for a property.
        Useful for getting the complete transaction history of a property.

        Args:
            listing_key: Property listing key to filter by
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing transactions for the specified property

        Example:
            ```python
            # Get all transactions for a property
            property_history = client.history.get_transactions_for_property(
                listing_key="1611952",
                orderby="CloseDate desc"
            )

            # Get sales only for a property
            property_sales = client.history.get_transactions_for_property(
                listing_key="1611952",
                filter_query="TransactionType eq 'Sale'",
                orderby="CloseDate desc"
            )
            ```
        """
        property_filter = f"ListingKey eq '{listing_key}'"

        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{property_filter} and {existing_filter}"
        else:
            kwargs["filter_query"] = property_filter

        return self.get_history_transactions(**kwargs)

    def get_sales_by_price_range(
        self,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get sales transactions within a price range.

        Convenience method to filter sales transactions by price range.
        Useful for market analysis and comparable sales research.

        Args:
            min_price: Minimum sale price filter
            max_price: Maximum sale price filter
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing sales within the specified price range

        Example:
            ```python
            # Get sales between $400K and $600K
            mid_range_sales = client.history.get_sales_by_price_range(
                min_price=400000,
                max_price=600000,
                orderby="CloseDate desc",
                top=100
            )

            # Get luxury sales above $1M
            luxury_sales = client.history.get_sales_by_price_range(
                min_price=1000000,
                orderby="ClosePrice desc"
            )
            ```
        """
        filters = ["TransactionType eq 'Sale'"]

        if min_price is not None:
            filters.append(f"ClosePrice ge {min_price}")
        if max_price is not None:
            filters.append(f"ClosePrice le {max_price}")

        price_filter = " and ".join(filters)

        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{price_filter} and {existing_filter}"
        else:
            kwargs["filter_query"] = price_filter

        return self.get_history_transactions(**kwargs)

    def get_sales_by_date_range(
        self,
        start_date: Union[str, date, datetime],
        end_date: Union[str, date, datetime],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get sales transactions within a date range.

        Convenience method to filter sales transactions by close date range.
        Useful for analyzing market activity in specific time periods.

        Args:
            start_date: Start date for filtering (inclusive)
            end_date: End date for filtering (inclusive)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing sales within the specified date range

        Example:
            ```python
            from datetime import date

            # Get sales from Q1 2023
            q1_sales = client.history.get_sales_by_date_range(
                start_date=date(2023, 1, 1),
                end_date=date(2023, 3, 31),
                orderby="CloseDate desc"
            )

            # Get sales from last 30 days
            from datetime import datetime, timedelta
            recent_sales = client.history.get_sales_by_date_range(
                start_date=datetime.now() - timedelta(days=30),
                end_date=datetime.now(),
                orderby="ClosePrice desc",
                top=100
            )
            ```
        """
        # Convert dates to ISO format
        if isinstance(start_date, (date, datetime)):
            start_str = start_date.isoformat()
        else:
            start_str = start_date

        if isinstance(end_date, (date, datetime)):
            end_str = end_date.isoformat()
        else:
            end_str = end_date

        date_filter = f"TransactionType eq 'Sale' and CloseDate ge '{start_str}' and CloseDate le '{end_str}'"

        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{date_filter} and {existing_filter}"
        else:
            kwargs["filter_query"] = date_filter

        return self.get_history_transactions(**kwargs)

    def get_recent_sales(self, days_back: int = 30, **kwargs: Any) -> Dict[str, Any]:
        """Get recent sales transactions.

        Convenience method to get sales from the last N days.
        Useful for current market activity analysis.

        Args:
            days_back: Number of days back to search (default: 30)
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing recent sales transactions

        Example:
            ```python
            # Get sales from last 7 days
            recent_week = client.history.get_recent_sales(
                days_back=7,
                orderby="CloseDate desc",
                top=50
            )

            # Get recent luxury sales
            recent_luxury = client.history.get_recent_sales(
                days_back=30,
                filter_query="ClosePrice gt 1000000",
                orderby="ClosePrice desc"
            )
            ```
        """
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=days_back)
        cutoff_str = cutoff_date.isoformat()

        recent_filter = f"TransactionType eq 'Sale' and CloseDate ge '{cutoff_str}'"

        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{recent_filter} and {existing_filter}"
        else:
            kwargs["filter_query"] = recent_filter

        return self.get_history_transactions(**kwargs)

    def get_transactions_by_city(self, city: str, **kwargs: Any) -> Dict[str, Any]:
        """Get transactions in a specific city.

        Convenience method to filter transactions by city name.
        Useful for location-specific market analysis.

        Args:
            city: City name to filter by
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing transactions in the specified city

        Example:
            ```python
            # Get Salt Lake City sales
            slc_sales = client.history.get_transactions_by_city(
                city="Salt Lake City",
                filter_query="TransactionType eq 'Sale'",
                orderby="CloseDate desc",
                top=100
            )
            ```
        """
        city_filter = f"City eq '{city}'"

        # If additional filter_query provided, combine them
        existing_filter = kwargs.get("filter_query")
        if existing_filter:
            kwargs["filter_query"] = f"{city_filter} and {existing_filter}"
        else:
            kwargs["filter_query"] = city_filter

        return self.get_history_transactions(**kwargs)

    def get_closed_transactions(self, **kwargs: Any) -> Dict[str, Any]:
        """Get transactions with Closed status.

        Convenience method to retrieve only closed transactions.
        Filters out pending, withdrawn, or other non-closed transactions.

        Args:
            **kwargs: Additional OData parameters (top, select, orderby, etc.)

        Returns:
            Dictionary containing closed transaction listings

        Example:
            ```python
            # Get all closed transactions
            closed_transactions = client.history.get_closed_transactions(
                orderby="CloseDate desc",
                top=100
            )

            # Get closed sales with price info
            closed_sales = client.history.get_closed_transactions(
                filter_query="TransactionType eq 'Sale'",
                select=["ListingKey", "ClosePrice", "CloseDate"],
                orderby="ClosePrice desc"
            )
            ```
        """
        return self.get_history_transactions(
            filter_query="Status eq 'Closed'", **kwargs
        )

    def get_transactions_with_property(self, **kwargs: Any) -> Dict[str, Any]:
        """Get transactions with their property information expanded.

        This is a convenience method that automatically expands the Property
        relationship to include property details in the response. More efficient
        than making separate requests for transactions and their properties.

        Args:
            **kwargs: OData parameters (top, filter_query, select, etc.)

        Returns:
            Dictionary containing transaction data with expanded Property relationships

        Example:
            ```python
            # Get recent transactions with property info
            transactions_with_props = client.history.get_transactions_with_property(
                filter_query="CloseDate gt '2023-01-01' and TransactionType eq 'Sale'",
                orderby="CloseDate desc",
                top=25
            )

            # Access property info for first transaction
            first_transaction = transactions_with_props['value'][0]
            if 'Property' in first_transaction:
                property_info = first_transaction['Property']
                print(f"Sold: {property_info['UnparsedAddress']}")
            ```
        """
        return self.get_history_transactions(expand="Property", **kwargs)

    def get_modified_transactions(
        self, since: Union[str, date, datetime], **kwargs: Any
    ) -> Dict[str, Any]:
        """Get transactions modified since a specific date/time.

        Used for incremental data synchronization to get only transaction records
        that have been updated since the last sync. Essential for maintaining
        up-to-date historical transaction information.

        Args:
            since: ISO format datetime string, date object, or datetime object for cutoff time
            **kwargs: Additional OData parameters

        Returns:
            Dictionary containing transactions modified since the specified time

        Example:
            ```python
            from datetime import datetime, timedelta

            # Get transactions modified in last 15 minutes (recommended sync interval)
            cutoff_time = datetime.utcnow() - timedelta(minutes=15)
            updates = client.history.get_modified_transactions(
                since=cutoff_time
            )

            # Get transactions modified since yesterday
            yesterday = datetime.utcnow() - timedelta(days=1)
            updates = client.history.get_modified_transactions(
                since=yesterday,
                orderby="ModificationTimestamp desc"
            )
            ```
        """
        if isinstance(since, datetime):
            since_str = since.isoformat() + "Z"
        elif isinstance(since, date):
            since_str = since.isoformat() + "T00:00:00Z"
        else:
            since_str = since

        filter_query = f"ModificationTimestamp gt '{since_str}'"
        return self.get_history_transactions(filter_query=filter_query, **kwargs)
