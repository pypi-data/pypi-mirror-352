"""
Integration tests for Helmut4 client.

These tests require a running Helmut4 server instance.
Set the following environment variables to run integration tests:
- HELMUT4_HOST (default: 192.168.0.211)
- HELMUT4_PORT (default: 80)
- HELMUT4_USERNAME (default: admin)
- HELMUT4_PASSWORD (default: admin)
"""

import os

import pytest

from helmut4.client import Helmut4Client, Helmut4Error


@pytest.fixture(scope="session")
def helmut4_config():
    """Configuration for Helmut4 server."""
    return {
        "host": os.getenv("HELMUT4_HOST", "192.168.0.211"),
        "port": int(os.getenv("HELMUT4_PORT", "80")),
        "username": os.getenv("HELMUT4_USERNAME", "admin"),
        "password": os.getenv("HELMUT4_PASSWORD", "admin"),
    }


@pytest.fixture(scope="session")
def helmut4_client(helmut4_config):
    """Helmut4 client instance for integration tests."""
    base_url = f"http://{helmut4_config['host']}:{helmut4_config['port']}"

    client = Helmut4Client(
        base_url=base_url,
        username=helmut4_config["username"],
        password=helmut4_config["password"],
    )

    return client


@pytest.mark.integration
class TestHelmut4Integration:
    """Integration tests for Helmut4 client."""

    def test_authentication(self, helmut4_client):
        """Test that authentication works."""
        assert helmut4_client.token is not None
        assert len(helmut4_client.token) > 50  # JWT tokens are typically long

    def test_get_users(self, helmut4_client):
        """Test getting users from the server."""
        users = helmut4_client.users.get_all(limit=10)

        assert isinstance(users, list)
        if users:  # If there are users
            user = users[0]
            assert "id" in user
            assert "username" in user
            assert "displayname" in user

    def test_get_admin_user_by_name(self, helmut4_client, helmut4_config):
        """Test getting the admin user by username."""
        admin_user = helmut4_client.users.get_by_name(
            helmut4_config["username"]
        )

        assert admin_user["username"] == helmut4_config["username"]
        assert "id" in admin_user
        assert "role" in admin_user

    def test_search_projects(self, helmut4_client):
        """Test searching for projects."""
        projects = helmut4_client.projects.search(limit=10)

        assert isinstance(projects, list)
        # Projects list might be empty, which is fine

    def test_search_assets(self, helmut4_client):
        """Test searching for assets."""
        assets = helmut4_client.assets.search(limit=10)

        assert isinstance(assets, list)
        # Assets list might be empty, which is fine

    def test_get_all_streams(self, helmut4_client):
        """Test getting all streams."""
        streams = helmut4_client.streams.get_all()

        assert isinstance(streams, list)
        # Streams list might be empty, which is fine

    def test_invalid_authentication(self, helmut4_config):
        """Test that invalid credentials raise an error."""
        base_url = f"http://{helmut4_config['host']}:{helmut4_config['port']}"

        with pytest.raises(Helmut4Error) as exc_info:
            Helmut4Client(
                base_url=base_url,
                username="invalid_user",
                password="invalid_password",
            )

        # Should contain authentication error information
        assert exc_info.value.status_code in [401, 403]

    def test_invalid_server_url(self):
        """Test that invalid server URL raises an error."""
        with pytest.raises(Helmut4Error):
            client = Helmut4Client(
                base_url="http://nonexistent.server.invalid:12345",
                username="admin",
                password="admin",
            )
            # Try to trigger authentication
            client.authenticate()


# Skip integration tests by default
pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION_TESTS") != "1",
    reason=
    "Integration tests require RUN_INTEGRATION_TESTS=1 environment variable",
)
