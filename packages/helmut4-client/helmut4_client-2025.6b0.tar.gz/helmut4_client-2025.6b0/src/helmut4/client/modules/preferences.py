"""
Preferences module for Helmut4 client.
"""

from typing import BinaryIO, Dict, List

from ._base import BaseModule


class PreferencesModule(BaseModule):
    """Module for managing system preferences"""

    def get_all(self) -> List[Dict]:
        """
        Get all preferences.

        Returns:
            List of preference objects
        """
        return self.client.request("GET", "/v1/preferences")

    def get_by_tags(self, tags: List[str]) -> List[Dict]:
        """
        Get preferences by tags.

        Args:
            tags: List of tags to filter by

        Returns:
            List of matching preference objects
        """
        return self.client.request("GET", f"/v1/preferences/{','.join(tags)}")

    def create(self, preference: Dict) -> Dict:
        """
        Create a new preference.

        Args:
            preference: Preference definition

        Returns:
            Created preference object
        """
        return self.client.request("POST", "/v1/preferences", json=preference)

    def update(self, preference: Dict) -> Dict:
        """
        Update an existing preference.

        Args:
            preference: Preference data including the ID

        Returns:
            Updated preference object
        """
        return self.client.request("PUT", "/v1/preferences", json=preference)

    def delete(self, preference_id: str) -> str:
        """
        Delete a preference.

        Args:
            preference_id: ID of the preference to delete

        Returns:
            Success message
        """
        return self.client.request("DELETE", f"/v1/preferences/{preference_id}")

    def get_storage(self) -> List[Dict]:
        """
        Get all storage mount points.

        Returns:
            List of storage objects
        """
        return self.client.request("GET", "/v1/storage")

    def add_storage(self, storage: Dict) -> Dict:
        """
        Add a new storage mount point.

        Args:
            storage: Storage mount point definition

        Returns:
            Created storage object
        """
        return self.client.request("POST", "/v1/storage", json=storage)

    def update_storage(self, storage: Dict) -> Dict:
        """
        Update a storage mount point.

        Args:
            storage: Storage mount point data including the ID

        Returns:
            Updated storage object
        """
        return self.client.request("PUT", "/v1/storage", json=storage)

    def delete_storage(self, storage_id: str) -> str:
        """
        Delete a storage mount point.

        Args:
            storage_id: ID of the storage mount point to delete

        Returns:
            Success message
        """
        return self.client.request("DELETE", f"/v1/storage/{storage_id}")

    def get_active_directory(self) -> Dict:
        """
        Get Active Directory configuration.

        Returns:
            Active Directory configuration
        """
        return self.client.request("GET", "/v1/activedirectory")

    def update_active_directory(self, ad_config: Dict) -> Dict:
        """
        Update Active Directory configuration.

        Args:
            ad_config: Active Directory configuration

        Returns:
            Updated Active Directory configuration
        """
        return self.client.request("PUT", "/v1/activedirectory", json=ad_config)

    def create_backup(self, databases: List[str]) -> bytes:
        """
        Create a system backup.

        Args:
            databases: List of databases to include in the backup

        Returns:
            Binary backup file content
        """
        return self.client.request("GET", f"/v1/backup/{','.join(databases)}")

    def restore_backup(self, backup_file: BinaryIO) -> Dict:
        """
        Restore a system from backup.

        Args:
            backup_file: Binary content or file handle of the backup file

        Returns:
            Restore result
        """
        files = {"file": backup_file}
        return self.client.request("POST", "/v1/restore", files=files)

    def test_module(self, module: str) -> int:
        """
        Test a module connection.

        Args:
            module: Module to test (FLOW, ACTIVE_DIRECTORY, MEDIALOOPSTER)

        Returns:
            Number of items found during test
        """
        return self.client.request("GET", f"/v1/preferences/test/{module}")
