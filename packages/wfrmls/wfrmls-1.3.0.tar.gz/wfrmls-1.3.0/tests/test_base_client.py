"""Tests for base client."""

import pytest
import responses
from requests.exceptions import ConnectionError, Timeout

from wfrmls.base_client import BaseClient
from wfrmls.exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    WFRMLSError,
)


class TestBaseClientInit:
    """Test BaseClient initialization."""

    def test_init_with_bearer_token(self) -> None:
        """Test initialization with provided bearer token."""
        client = BaseClient(bearer_token="test_token")
        assert client.bearer_token == "test_token"
        assert client.base_url == "https://resoapi.utahrealestate.com/reso/odata"

    def test_init_with_custom_base_url(self) -> None:
        """Test initialization with custom base URL."""
        client = BaseClient(
            bearer_token="test_token", 
            base_url="https://custom.api.com"
        )
        assert client.base_url == "https://custom.api.com"

    def test_init_with_env_token(self) -> None:
        """Test initialization loading token from environment."""
        import os
        # Save original value
        original_token = os.environ.get("WFRMLS_BEARER_TOKEN")
        
        try:
            # Set environment variable
            os.environ["WFRMLS_BEARER_TOKEN"] = "env_test_token"
            client = BaseClient()
            assert client.bearer_token == "env_test_token"
        finally:
            # Restore original value
            if original_token is not None:
                os.environ["WFRMLS_BEARER_TOKEN"] = original_token
            elif "WFRMLS_BEARER_TOKEN" in os.environ:
                del os.environ["WFRMLS_BEARER_TOKEN"]

    def test_init_no_token_raises_error(self) -> None:
        """Test initialization without token raises AuthenticationError."""
        import os
        # Save original value
        original_token = os.environ.get("WFRMLS_BEARER_TOKEN")
        
        try:
            # Remove environment variable
            if "WFRMLS_BEARER_TOKEN" in os.environ:
                del os.environ["WFRMLS_BEARER_TOKEN"]
            
            with pytest.raises(AuthenticationError, match="Bearer token is required"):
                BaseClient()
        finally:
            # Restore original value
            if original_token is not None:
                os.environ["WFRMLS_BEARER_TOKEN"] = original_token


class TestBaseClient:
    """Test BaseClient HTTP methods."""

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = BaseClient(bearer_token="test_bearer_token")

    @responses.activate
    def test_get_success(self) -> None:
        """Test successful GET request."""
        mock_response = {"test": "data"}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            json=mock_response,
            status=200,
        )

        result = self.client.get("TestEndpoint")
        assert result == mock_response
        assert len(responses.calls) == 1

        # Verify headers
        request = responses.calls[0].request
        assert request.headers["Authorization"] == "Bearer test_bearer_token"
        assert request.headers["Accept"] == "application/json"

    @responses.activate
    def test_get_with_params(self) -> None:
        """Test GET request with parameters."""
        mock_response = {"test": "data"}

        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            json=mock_response,
            status=200,
        )

        params = {"$top": 10, "$filter": "Status eq 'Active'"}
        result = self.client.get("TestEndpoint", params=params)
        assert result == mock_response

        # Verify URL parameters
        request = responses.calls[0].request
        assert request.url is not None
        assert "%24top=10" in request.url
        assert "Status+eq+%27Active%27" in request.url or "Status eq 'Active'" in request.url

    @responses.activate
    def test_validation_error_400(self) -> None:
        """Test 400 Bad Request raises ValidationError."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            json={"error": {"message": "Invalid request"}},
            status=400,
        )

        with pytest.raises(ValidationError, match="Bad request: Invalid request"):
            self.client.get("TestEndpoint")

    @responses.activate
    def test_authentication_error_401(self) -> None:
        """Test 401 Unauthorized raises AuthenticationError."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            json={"error": {"message": "Invalid credentials"}},
            status=401,
        )

        with pytest.raises(AuthenticationError, match="Authentication failed: Invalid credentials"):
            self.client.get("TestEndpoint")

    @responses.activate
    def test_not_found_error_404(self) -> None:
        """Test 404 Not Found raises NotFoundError."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            json={"error": {"message": "Resource not found"}},
            status=404,
        )

        with pytest.raises(NotFoundError, match="Resource not found: Resource not found"):
            self.client.get("TestEndpoint")

    @responses.activate
    def test_rate_limit_error_429(self) -> None:
        """Test 429 Too Many Requests raises RateLimitError."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            json={"error": {"message": "Rate limit exceeded"}},
            status=429,
        )

        with pytest.raises(RateLimitError, match="Rate limit exceeded: Rate limit exceeded"):
            self.client.get("TestEndpoint")

    @responses.activate
    def test_server_error_500(self) -> None:
        """Test 500 Internal Server Error raises ServerError."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            json={"error": {"message": "Internal server error"}},
            status=500,
        )

        with pytest.raises(ServerError, match="Server error: Internal server error"):
            self.client.get("TestEndpoint")

    @responses.activate
    def test_server_error_503(self) -> None:
        """Test 503 Service Unavailable raises ServerError."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            json={"error": {"message": "Service unavailable"}},
            status=503,
        )

        with pytest.raises(ServerError, match="Server error: Service unavailable"):
            self.client.get("TestEndpoint")

    @responses.activate
    def test_no_content_204(self) -> None:
        """Test 204 No Content returns empty dict."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            status=204,
        )

        result = self.client.get("TestEndpoint")
        assert result == {}

    @responses.activate
    def test_invalid_json_response(self) -> None:
        """Test response with invalid JSON."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            body="Invalid JSON",
            status=200,
            content_type="text/plain"
        )

        result = self.client.get("TestEndpoint")
        assert result == {"message": "Invalid JSON"}

    @responses.activate
    def test_network_error_connection(self) -> None:
        """Test connection error raises NetworkError."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            body=ConnectionError("Connection failed")
        )

        with pytest.raises(NetworkError, match="Network error: Connection failed"):
            self.client.get("TestEndpoint")

    @responses.activate
    def test_network_error_timeout(self) -> None:
        """Test timeout error raises NetworkError."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            body=Timeout("Request timed out")
        )

        with pytest.raises(NetworkError, match="Network error: Request timed out"):
            self.client.get("TestEndpoint")

    @responses.activate
    def test_unknown_error_status(self) -> None:
        """Test unknown error status raises WFRMLSError."""
        responses.add(
            responses.GET,
            "https://resoapi.utahrealestate.com/reso/odata/TestEndpoint",
            json={"error": {"message": "Unknown error"}},
            status=418,  # I'm a teapot
        )

        with pytest.raises(WFRMLSError, match="Unexpected error"):
            self.client.get("TestEndpoint")

    def test_session_headers(self) -> None:
        """Test that session headers are set correctly."""
        assert self.client.session.headers["Authorization"] == "Bearer test_bearer_token"
        assert self.client.session.headers["Content-Type"] == "application/json"
        assert self.client.session.headers["Accept"] == "application/json"

    def test_custom_base_url_session(self) -> None:
        """Test session with custom base URL."""
        client = BaseClient(
            bearer_token="test", 
            base_url="https://custom.api.com/api"
        )
        assert client.base_url == "https://custom.api.com/api"
        assert client.session.headers["Authorization"] == "Bearer test" 