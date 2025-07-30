"""
Groups module for Helmut4 client.
"""

from typing import Dict, List

from ._base import BaseModule


class GroupsModule(BaseModule):
    """Module for managing groups"""

    def get_all(self) -> List[Dict]:
        """
        Get all groups.

        Returns:
            List of group objects
        """
        return self.client.request("GET", "/v1/members/groups")

    def get_by_id(self, group_id: str) -> Dict:
        """
        Get a group by ID.

        Args:
            group_id: The ID of the group

        Returns:
            Group object
        """
        return self.client.request("GET", f"/v1/members/groups/{group_id}")

    def get_by_name(self, group_name: str) -> Dict:
        """
        Get a group by name.

        Args:
            group_name: The name of the group

        Returns:
            Group object
        """
        return self.client.request(
            "GET", f"/v1/members/groups/name/{group_name}"
        )

    def create(self, group_data: Dict) -> Dict:
        """
        Create a new group.

        Args:
            group_data: Group data including at minimum:
                - name: Group name

        Returns:
            Created group object
        """
        return self.client.request(
            "POST", "/v1/members/groups", json=group_data
        )

    def update(self, group_data: Dict) -> Dict:
        """
        Update an existing group.

        Args:
            group_data: Group data to update including the ID

        Returns:
            Updated group object
        """
        return self.client.request("PUT", "/v1/members/groups", json=group_data)

    def delete(self, group_id: str) -> str:
        """
        Delete a group.

        Args:
            group_id: ID of the group to delete

        Returns:
            Success message
        """
        return self.client.request("DELETE", f"/v1/members/groups/{group_id}")

    def get_users(self, group_id: str) -> List[Dict]:
        """
        Get all users in a group.

        Args:
            group_id: ID of the group

        Returns:
            List of user objects in the group
        """
        return self.client.request("GET", f"/v1/members/users/group/{group_id}")

    def update_custom_field(self, group_data: Dict) -> Dict:
        """
        Update a group's custom field.

        Args:
            group_data: Group data with custom field to update

        Returns:
            Updated group object
        """
        return self.client.request(
            "PUT", "/v1/members/groups/change/custom", json=group_data
        )
