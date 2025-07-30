"""
Metadata module for Helmut4 client.
"""

from typing import Dict, List

from ._base import BaseModule


class MetadataModule(BaseModule):
    """Module for managing metadata"""

    def get_all(self) -> List[Dict]:
        """
        Get all metadata.

        Returns:
            List of metadata objects
        """
        return self.client.request("GET", "/v1/metadata")

    def get_by_tags(self, tags: List[str]) -> List[Dict]:
        """
        Get metadata by tags.

        Args:
            tags: List of tags to filter by

        Returns:
            List of matching metadata objects
        """
        return self.client.request("GET", f"/v1/metadata/{','.join(tags)}")

    def create(self, metadata: Dict) -> Dict:
        """
        Create a new metadata field.

        Args:
            metadata: Metadata definition

        Returns:
            Created metadata object
        """
        return self.client.request("POST", "/v1/metadata", json=metadata)

    def update(self, metadata: Dict) -> Dict:
        """
        Update an existing metadata field.

        Args:
            metadata: Metadata data including the ID

        Returns:
            Updated metadata object
        """
        return self.client.request("PUT", "/v1/metadata", json=metadata)

    def delete(self, metadata_id: str) -> str:
        """
        Delete a metadata field.

        Args:
            metadata_id: ID of the metadata to delete

        Returns:
            Success message
        """
        return self.client.request("DELETE", f"/v1/metadata/{metadata_id}")

    def get_all_sets(self) -> List[Dict]:
        """
        Get all metadata sets.

        Returns:
            List of metadata set objects
        """
        return self.client.request("GET", "/v1/metadataSet")

    def get_sets_by_tags(self, tags: List[str]) -> List[Dict]:
        """
        Get metadata sets by tags.

        Args:
            tags: List of tags to filter by

        Returns:
            List of matching metadata set objects
        """
        return self.client.request("GET", f"/v1/metadataSet/{','.join(tags)}")

    def create_set(self, metadata_set: Dict) -> Dict:
        """
        Create a new metadata set.

        Args:
            metadata_set: Metadata set definition

        Returns:
            Created metadata set object
        """
        return self.client.request("POST", "/v1/metadataSet", json=metadata_set)

    def create_fx_group_set(self, metadata_set: Dict) -> Dict:
        """
        Create a new metadata set as FX group.

        Args:
            metadata_set: Metadata set definition

        Returns:
            Created metadata set object
        """
        return self.client.request(
            "POST", "/v1/metadataSet/fxGroup", json=metadata_set
        )

    def update_set(self, metadata_set: Dict) -> Dict:
        """
        Update an existing metadata set.

        Args:
            metadata_set: Metadata set data including the ID

        Returns:
            Updated metadata set object
        """
        return self.client.request("PUT", "/v1/metadataSet", json=metadata_set)

    def delete_set(self, metadata_set_id: str) -> str:
        """
        Delete a metadata set.

        Args:
            metadata_set_id: ID of the metadata set to delete

        Returns:
            Success message
        """
        return self.client.request(
            "DELETE", f"/v1/metadataSet/{metadata_set_id}"
        )

    def add_parent(self, metadata_id: str, parent_set: Dict) -> Dict:
        """
        Add a parent to a metadata field.

        Args:
            metadata_id: ID of the metadata field
            parent_set: Parent metadata set to add

        Returns:
            Updated metadata object
        """
        return self.client.request(
            "PUT",
            f"/v1/metadata/parent/{metadata_id}?add=true",
            json=parent_set,
        )

    def remove_parent(self, metadata_id: str, parent_set: Dict) -> Dict:
        """
        Remove a parent from a metadata field.

        Args:
            metadata_id: ID of the metadata field
            parent_set: Parent metadata set to remove

        Returns:
            Updated metadata object
        """
        return self.client.request(
            "PUT",
            f"/v1/metadata/parent/{metadata_id}?add=false",
            json=parent_set,
        )

    def update_parents(self, metadata_id: str, parent_sets: List[Dict]) -> Dict:
        """
        Update all parents of a metadata field.

        Args:
            metadata_id: ID of the metadata field
            parent_sets: List of parent metadata sets

        Returns:
            Updated metadata object
        """
        return self.client.request(
            "POST", f"/v1/metadata/parent/{metadata_id}", json=parent_sets
        )
