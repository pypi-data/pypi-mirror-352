"""
Users module for Helmut4 client.
"""

from typing import Dict, List

from ._base import BaseModule


class UsersModule(BaseModule):
    """Module for managing users"""

    def get_all(
        self,
        group_filter: str = "All",
        limit: int = 500,
        page: int = 0
    ) -> List[Dict]:
        """
        Get all users, optionally filtered by group.

        Args:
            group_filter: Filter users by group (All, Unassigned, or a group ID)
            limit: Maximum number of results
            page: Page number for pagination

        Returns:
            List of user objects
        """
        # pylint: disable=line-too-long
        return self.client.request(
            "GET",
            f"/v1/members/users/search?groupFilter={group_filter}&limit={limit}&page={page}",
        )

    def get_by_id(self, user_id: str) -> Dict:
        """
        Get a user by ID.

        Args:
            user_id: The ID of the user

        Returns:
            User object
        """
        return self.client.request("GET", f"/v1/members/users/{user_id}")

    def get_by_name(self, username: str) -> Dict:
        """
        Get a user by username.

        Args:
            username: The username to look up

        Returns:
            User object
        """
        return self.client.request("GET", f"/v1/members/users/name/{username}")

    def create(self, user_data: Dict) -> Dict:
        """
        Create a new user.

        Args:
            user_data: User data including at minimum:
                - username: Username
                - password: Password
                - displayname: Display name
                - role: User role (Admin, User, etc.)

        Returns:
            Created user object
        """
        return self.client.request("POST", "/v1/members/users", json=user_data)

    def update(self, user_id: str, user_data: Dict) -> Dict:
        """
        Update an existing user.

        Args:
            user_id: ID of the user to update
            user_data: User data to update

        Returns:
            Updated user object
        """
        return self.client.request(
            "PUT", f"/v1/members/users/{user_id}", json=user_data
        )

    def delete(self, user_id: str) -> str:
        """
        Delete a user.

        Args:
            user_id: ID of the user to delete

        Returns:
            Success message
        """
        return self.client.request("DELETE", f"/v1/members/users/{user_id}")

    def add_to_group(self, user_id: str, group_id: str) -> Dict:
        """
        Add a user to a group.

        Args:
            user_id: ID of the user
            group_id: ID of the group

        Returns:
            Updated user object
        """
        data = {"userId": user_id, "groupId": group_id}
        return self.client.request(
            "PUT", "/v1/members/users/group/add", json=data
        )

    def remove_from_group(self, user_id: str, group_id: str) -> Dict:
        """
        Remove a user from a group.

        Args:
            user_id: ID of the user
            group_id: ID of the group

        Returns:
            Updated user object
        """
        data = {"userId": user_id, "groupId": group_id}
        return self.client.request(
            "PUT", "/v1/members/users/group/del", json=data
        )

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> Dict:
        """
        Change a user's password.

        Args:
            user_id: ID of the user
            old_password: Current password
            new_password: New password

        Returns:
            Updated user object
        """
        data = {
            "id": user_id,
            "oldPassword": old_password,
            "newPassword": new_password,
        }
        return self.client.request(
            "PUT", "/v1/members/users/change/password", json=data
        )

    def get_connected_users(self) -> List[Dict]:
        """
        Get all currently connected users.

        Returns:
            List of connected user objects
        """
        return self.client.request("GET", "/v1/members/users/connected")

    def notify_user(self, username: str, message: Dict) -> Dict:
        """
        Send a notification to a user.

        Args:
            username: Username of the recipient (or * for all users)
            message: Message object with title and body

        Returns:
            Result object
        """
        return self.client.request(
            "POST", f"/v1/members/users/notification/{username}", json=message
        )

    def kick_user(self, username: str, client_session_id: str = None) -> Dict:
        """
        Kick a user from the system.

        Args:
            username: Username of the user to kick
            client_session_id: Optional client session ID for verifying the
                request

        Returns:
            Result object
        """
        params = {}
        if client_session_id:
            params = {"clientSessionId": client_session_id}

        return self.client.request(
            "GET", f"/v1/members/users/kick/{username}", params=params
        )
