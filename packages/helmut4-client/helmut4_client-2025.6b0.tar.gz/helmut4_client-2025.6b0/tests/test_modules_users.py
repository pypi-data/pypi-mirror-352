"""
Unit tests for UsersModule.
"""

from unittest.mock import Mock

import pytest

from helmut4.client.modules.users import UsersModule


class TestUsersModule:
    """Test UsersModule functionality."""

    @pytest.fixture
    def mock_client(self):
        """Mock client for testing."""
        client = Mock()
        client.request = Mock()
        return client

    @pytest.fixture
    def users_module(self, mock_client):
        """UsersModule instance for testing."""
        return UsersModule(mock_client)

    def test_get_all_default_params(
        self, users_module, mock_client, sample_user_data
    ):
        """Test get_all with default parameters."""
        mock_client.request.return_value = [sample_user_data]

        result = users_module.get_all()

        assert result == [sample_user_data]
        mock_client.request.assert_called_once_with(
            "GET", "/v1/members/users/search?groupFilter=All&limit=500&page=0"
        )

    def test_get_all_custom_params(self, users_module, mock_client):
        """Test get_all with custom parameters."""
        mock_client.request.return_value = []

        result = users_module.get_all(
            group_filter="Unassigned", limit=100, page=2
        )

        assert result == []
        mock_client.request.assert_called_once_with(
            "GET",
            "/v1/members/users/search?groupFilter=Unassigned&limit=100&page=2",
        )

    def test_get_by_id(self, users_module, mock_client, sample_user_data):
        """Test get_by_id method."""
        mock_client.request.return_value = sample_user_data

        result = users_module.get_by_id("user123")

        assert result == sample_user_data
        mock_client.request.assert_called_once_with(
            "GET", "/v1/members/users/user123"
        )

    def test_get_by_name(self, users_module, mock_client, sample_user_data):
        """Test get_by_name method."""
        mock_client.request.return_value = sample_user_data

        result = users_module.get_by_name("testuser")

        assert result == sample_user_data
        mock_client.request.assert_called_once_with(
            "GET", "/v1/members/users/name/testuser"
        )

    def test_create(self, users_module, mock_client, sample_user_data):
        """Test create method."""
        user_data = {
            "username": "newuser",
            "password": "password123",
            "displayname": "New User",
            "role": "User",
        }
        mock_client.request.return_value = sample_user_data

        result = users_module.create(user_data)

        assert result == sample_user_data
        mock_client.request.assert_called_once_with(
            "POST", "/v1/members/users", json=user_data
        )

    def test_update(self, users_module, mock_client, sample_user_data):
        """Test update method."""
        update_data = {"displayname": "Updated User"}
        mock_client.request.return_value = sample_user_data

        result = users_module.update("user123", update_data)

        assert result == sample_user_data
        mock_client.request.assert_called_once_with(
            "PUT", "/v1/members/users/user123", json=update_data
        )

    def test_delete(self, users_module, mock_client):
        """Test delete method."""
        mock_client.request.return_value = "User deleted successfully"

        result = users_module.delete("user123")

        assert result == "User deleted successfully"
        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/members/users/user123"
        )

    def test_add_to_group(self, users_module, mock_client, sample_user_data):
        """Test add_to_group method."""
        mock_client.request.return_value = sample_user_data

        result = users_module.add_to_group("user123", "group456")

        assert result == sample_user_data
        mock_client.request.assert_called_once_with(
            "PUT",
            "/v1/members/users/group/add",
            json={
                "userId": "user123",
                "groupId": "group456"
            },
        )

    def test_remove_from_group(
        self, users_module, mock_client, sample_user_data
    ):
        """Test remove_from_group method."""
        mock_client.request.return_value = sample_user_data

        result = users_module.remove_from_group("user123", "group456")

        assert result == sample_user_data
        mock_client.request.assert_called_once_with(
            "PUT",
            "/v1/members/users/group/del",
            json={
                "userId": "user123",
                "groupId": "group456"
            },
        )

    def test_change_password(self, users_module, mock_client, sample_user_data):
        """Test change_password method."""
        mock_client.request.return_value = sample_user_data

        result = users_module.change_password("user123", "oldpass", "newpass")

        assert result == sample_user_data
        mock_client.request.assert_called_once_with(
            "PUT",
            "/v1/members/users/change/password",
            json={
                "id": "user123",
                "oldPassword": "oldpass",
                "newPassword": "newpass",
            },
        )

    def test_get_connected_users(self, users_module, mock_client):
        """Test get_connected_users method."""
        connected_users = [
            {
                "id": "user1",
                "username": "user1",
                "connected": True
            },
            {
                "id": "user2",
                "username": "user2",
                "connected": True
            },
        ]
        mock_client.request.return_value = connected_users

        result = users_module.get_connected_users()

        assert result == connected_users
        mock_client.request.assert_called_once_with(
            "GET", "/v1/members/users/connected"
        )

    def test_notify_user(self, users_module, mock_client):
        """Test notify_user method."""
        message = {"title": "Test Notification", "body": "Test message"}
        mock_client.request.return_value = {"success": True}

        result = users_module.notify_user("testuser", message)

        assert result == {"success": True}
        mock_client.request.assert_called_once_with(
            "POST", "/v1/members/users/notification/testuser", json=message
        )

    def test_notify_all_users(self, users_module, mock_client):
        """Test notify_user with wildcard for all users."""
        message = {"title": "Broadcast", "body": "Message for all"}
        mock_client.request.return_value = {"success": True}

        result = users_module.notify_user("*", message)

        assert result == {"success": True}
        mock_client.request.assert_called_once_with(
            "POST", "/v1/members/users/notification/*", json=message
        )

    def test_kick_user_no_session_id(self, users_module, mock_client):
        """Test kick_user without session ID."""
        mock_client.request.return_value = {"success": True}

        result = users_module.kick_user("testuser")

        assert result == {"success": True}
        mock_client.request.assert_called_once_with(
            "GET", "/v1/members/users/kick/testuser", params={}
        )

    def test_kick_user_with_session_id(self, users_module, mock_client):
        """Test kick_user with session ID."""
        mock_client.request.return_value = {"success": True}

        result = users_module.kick_user("testuser", "session123")

        assert result == {"success": True}
        mock_client.request.assert_called_once_with(
            "GET",
            "/v1/members/users/kick/testuser",
            params={"clientSessionId": "session123"},
        )
