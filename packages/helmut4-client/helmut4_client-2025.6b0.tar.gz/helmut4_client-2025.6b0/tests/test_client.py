"""
Unit tests for the main Helmut4Client class.
"""

from unittest.mock import Mock, patch

import pytest
import requests

from helmut4.client import Helmut4Client, Helmut4Error


class TestHelmut4ClientInit:
    """Test Helmut4Client initialization."""

    def test_init_no_auth(self, base_url):
        """Test client initialization without authentication."""
        with patch("helmut4.client.client.requests.Session"):
            client = Helmut4Client(base_url=base_url)

            assert client.base_url == base_url
            assert client.username is None
            assert client.password is None
            assert client.token is None
            assert hasattr(client, "session")

            # Verify all modules are initialized
            assert hasattr(client, "users")
            assert hasattr(client, "groups")
            assert hasattr(client, "projects")
            assert hasattr(client, "assets")
            assert hasattr(client, "jobs")
            assert hasattr(client, "streams")
            assert hasattr(client, "metadata")
            assert hasattr(client, "preferences")
            assert hasattr(client, "cronjobs")
            assert hasattr(client, "languages")
            assert hasattr(client, "licenses")

    def test_init_with_token(self, base_url, auth_credentials):
        """Test client initialization with token authentication."""
        with patch(
            "helmut4.client.client.requests.Session"
        ) as mock_session_class:
            mock_session = Mock()
            mock_session.headers = Mock()
            mock_session.headers.update = Mock()
            mock_session_class.return_value = mock_session

            client = Helmut4Client(
                base_url=base_url, token=auth_credentials["token"]
            )

            assert client.token == auth_credentials["token"]
            mock_session.headers.update.assert_called_with({
                "Authorization": f"Bearer {auth_credentials['token']}"
            })

    def test_init_with_credentials_successful_auth(
        self, base_url, auth_credentials
    ):
        """Test client initialization with username/password authentication."""
        with patch(
            "helmut4.client.client.requests.Session"
        ) as mock_session_class:
            mock_session = Mock()
            mock_session.headers = {}

            # Mock successful authentication
            mock_response = Mock()
            mock_response.raise_for_status = Mock()
            mock_response.headers = {
                "Authorization": f"Bearer {auth_credentials['token']}"
            }
            mock_response.json.return_value = {"success": True}
            mock_session.post.return_value = mock_response

            mock_session_class.return_value = mock_session

            client = Helmut4Client(
                base_url=base_url,
                username=auth_credentials["username"],
                password=auth_credentials["password"],
            )

            assert client.username == auth_credentials["username"]
            assert client.password == auth_credentials["password"]
            assert client.token == auth_credentials["token"]

            # Verify authentication was called
            mock_session.post.assert_called_once()
            auth_call = mock_session.post.call_args
            assert "/v1/members/auth/login/body" in auth_call[0][0]
            assert (
                auth_call[1]["json"]["username"] == auth_credentials["username"]
            )
            assert (
                auth_call[1]["json"]["password"] == auth_credentials["password"]
            )

    def test_base_url_trailing_slash_removed(self):
        """Test that trailing slash is removed from base URL."""
        with patch("helmut4.client.client.requests.Session"):
            client = Helmut4Client(base_url="https://example.com/")
            assert client.base_url == "https://example.com"


class TestHelmut4ClientAuthentication:
    """Test authentication methods."""

    def test_authenticate_success_token_in_header(
        self, client_no_auth, auth_credentials
    ):
        """Test successful authentication with token in header."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {
            "Authorization": f"Bearer {auth_credentials['token']}"
        }
        mock_response.json.return_value = {"success": True}

        client_no_auth.username = auth_credentials["username"]
        client_no_auth.password = auth_credentials["password"]
        client_no_auth.session.post.return_value = mock_response

        token = client_no_auth.authenticate()

        assert token == auth_credentials["token"]
        assert client_no_auth.token == auth_credentials["token"]
        # Note: In fixtures, session.headers is a real dict, so update is not mockable

    def test_authenticate_success_token_in_body(
        self, client_no_auth, auth_credentials
    ):
        """Test successful authentication with token in response body."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {}
        mock_response.json.return_value = {"token": auth_credentials["token"]}

        client_no_auth.username = auth_credentials["username"]
        client_no_auth.password = auth_credentials["password"]
        client_no_auth.session.post.return_value = mock_response

        token = client_no_auth.authenticate()

        assert token == auth_credentials["token"]
        assert client_no_auth.token == auth_credentials["token"]

    def test_authenticate_no_token_error(
        self, client_no_auth, auth_credentials
    ):
        """Test authentication failure when no token is received."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {}
        mock_response.json.return_value = {"success": True}

        client_no_auth.username = auth_credentials["username"]
        client_no_auth.password = auth_credentials["password"]
        client_no_auth.session.post.return_value = mock_response

        with pytest.raises(Helmut4Error) as exc_info:
            client_no_auth.authenticate()

        assert "no token received" in str(exc_info.value)

    def test_authenticate_http_error(self, client_no_auth, auth_credentials):
        """Test authentication failure with HTTP error."""
        error_response = Mock()
        error_response.status_code = 401
        error_response.json.return_value = {"error": "Unauthorized"}

        http_error = requests.exceptions.HTTPError()
        http_error.response = error_response

        client_no_auth.username = auth_credentials["username"]
        client_no_auth.password = auth_credentials["password"]
        client_no_auth.session.post.side_effect = http_error

        with pytest.raises(Helmut4Error) as exc_info:
            client_no_auth.authenticate()

        assert exc_info.value.status_code == 401
        assert exc_info.value.response == {"error": "Unauthorized"}

    def test_authenticate_connection_error(
        self, client_no_auth, auth_credentials
    ):
        """Test authentication failure with connection error."""
        client_no_auth.username = auth_credentials["username"]
        client_no_auth.password = auth_credentials["password"]
        client_no_auth.session.post.side_effect = (
            requests.exceptions.ConnectionError("Connection failed")
        )

        with pytest.raises(Helmut4Error) as exc_info:
            client_no_auth.authenticate()

        assert "Connection failed" in str(exc_info.value)
        assert exc_info.value.status_code is None


class TestHelmut4ClientRequest:
    """Test request method."""

    def test_request_success_json(self, client_no_auth):
        """Test successful request returning JSON."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"data": "test"}

        client_no_auth.session.request.return_value = mock_response

        result = client_no_auth.request("GET", "/test/path")

        assert result == {"data": "test"}
        client_no_auth.session.request.assert_called_once_with(
            "GET", f"{client_no_auth.base_url}/test/path"
        )

    def test_request_success_binary(self, client_no_auth):
        """Test successful request returning binary data."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {"Content-Type": "application/octet-stream"}
        mock_response.content = b"binary data"

        client_no_auth.session.request.return_value = mock_response

        result = client_no_auth.request("GET", "/download/file")

        assert result == b"binary data"

    def test_request_success_text_fallback(self, client_no_auth):
        """Test successful request falling back to text when JSON fails."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_response.json.side_effect = ValueError("No JSON object")
        mock_response.text = "plain text response"

        client_no_auth.session.request.return_value = mock_response

        result = client_no_auth.request("GET", "/text/endpoint")

        assert result == "plain text response"

    def test_request_with_parameters(self, client_no_auth):
        """Test request with additional parameters."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"data": "test"}

        client_no_auth.session.request.return_value = mock_response

        result = client_no_auth.request(
            "POST",
            "/api/endpoint",
            json={"key": "value"},
            params={"filter": "test"},
        )

        assert result == {"data": "test"}
        client_no_auth.session.request.assert_called_once_with(
            "POST",
            f"{client_no_auth.base_url}/api/endpoint",
            json={"key": "value"},
            params={"filter": "test"},
        )

    def test_request_http_error_with_json_response(self, client_no_auth):
        """Test request failure with JSON error response."""
        error_response = Mock()
        error_response.status_code = 404
        error_response.json.return_value = {"error": "Not Found"}

        http_error = requests.exceptions.HTTPError()
        http_error.response = error_response

        client_no_auth.session.request.side_effect = http_error

        with pytest.raises(Helmut4Error) as exc_info:
            client_no_auth.request("GET", "/nonexistent")

        assert exc_info.value.status_code == 404
        assert exc_info.value.response == {"error": "Not Found"}

    def test_request_http_error_with_text_response(self, client_no_auth):
        """Test request failure with text error response."""
        error_response = Mock()
        error_response.status_code = 500
        error_response.json.side_effect = requests.exceptions.JSONDecodeError(
            "test", "test", 0
        )
        error_response.text = "Internal Server Error"

        http_error = requests.exceptions.HTTPError()
        http_error.response = error_response

        client_no_auth.session.request.side_effect = http_error

        with pytest.raises(Helmut4Error) as exc_info:
            client_no_auth.request("GET", "/error")

        assert exc_info.value.status_code == 500
        assert exc_info.value.response == {"error": "Internal Server Error"}

    def test_request_connection_error(self, client_no_auth):
        """Test request failure with connection error."""
        client_no_auth.session.request.side_effect = (
            requests.exceptions.ConnectionError("Connection failed")
        )

        with pytest.raises(Helmut4Error) as exc_info:
            client_no_auth.request("GET", "/test")

        assert "Connection failed" in str(exc_info.value)
        assert exc_info.value.status_code is None


class TestHelmut4ClientModuleIntegration:
    """Test integration with API modules."""

    def test_modules_have_client_reference(self, client_no_auth):
        """Test that all modules have reference to client."""
        modules = [
            client_no_auth.users,
            client_no_auth.groups,
            client_no_auth.projects,
            client_no_auth.assets,
            client_no_auth.jobs,
            client_no_auth.streams,
            client_no_auth.metadata,
            client_no_auth.preferences,
            client_no_auth.cronjobs,
            client_no_auth.languages,
            client_no_auth.licenses,
        ]

        for module in modules:
            assert hasattr(module, "client")
            assert module.client is client_no_auth

    def test_module_can_make_requests(self, client_no_auth):
        """Test that modules can make requests through client."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = [{"id": "user1", "name": "Test User"}]

        client_no_auth.session.request.return_value = mock_response

        # Test through users module
        result = client_no_auth.users.get_all()

        assert result == [{"id": "user1", "name": "Test User"}]
        client_no_auth.session.request.assert_called_once()
        call_args = client_no_auth.session.request.call_args
        assert "users/search" in call_args[0][1]
