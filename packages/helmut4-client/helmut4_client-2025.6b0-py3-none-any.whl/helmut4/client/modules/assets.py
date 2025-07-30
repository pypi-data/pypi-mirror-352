"""
Assets module for Helmut4 client.
"""

from typing import Any, Dict, List, Optional

from ._base import BaseModule


class AssetsModule(BaseModule):
    """Module for managing assets"""

    def search(
        self,
        search_filter: Optional[Dict] = None,
        limit: int = 500,
        page: int = 0,
        project_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        Search for assets based on a filter.

        Args:
            search_filter: Search filter criteria
            limit: Maximum number of results
            page: Page number for pagination
            project_id: Optional project ID to filter by

        Returns:
            List of matching asset objects
        """
        params: Dict[str, Any] = {"limit": limit, "page": page}
        if project_id:
            params["projectId"] = project_id

        return self.client.request(
            "POST", "/v1/co/search", params=params, json=search_filter or {}
        )

    def get_by_id(self, asset_id: str) -> Dict:
        """
        Get an asset by ID.

        Args:
            asset_id: The ID of the asset

        Returns:
            Asset object
        """
        return self.client.request(
            "GET", "/v1/co/assets", params={"assetId": asset_id}
        )

    def get_by_project_id(self, project_id: str) -> List[Dict]:
        """
        Get all assets for a project.

        Args:
            project_id: The ID of the project

        Returns:
            List of asset objects
        """
        return self.client.request("GET", f"/v1/co/assets/{project_id}")

    def create(
        self, asset_data: Dict, create_bin_structure: bool = True
    ) -> Dict:
        """
        Create a new asset.

        Args:
            asset_data: Asset data
            create_bin_structure: Whether to create parent bins according to
                assetBreadCrumb

        Returns:
            Created asset object
        """
        params = {"createBinStructure": str(create_bin_structure).lower()}
        return self.client.request(
            "POST", "/v1/co/assets", params=params, json=asset_data
        )

    def update(self, asset_data: Dict) -> Dict:
        """
        Update an existing asset.

        Args:
            asset_data: Asset data including the ID

        Returns:
            Updated asset object
        """
        return self.client.request("PUT", "/v1/co/assets", json=asset_data)

    def patch(self, asset_data: Dict) -> Dict:
        """
        Update specific fields of an existing asset.

        Args:
            asset_data: Asset data with the fields to update (must include ID)

        Returns:
            Updated asset object
        """
        return self.client.request("PATCH", "/v1/co/assets", json=asset_data)

    def delete(
        self, asset_ids: List[str], project_id: Optional[str] = None
    ) -> Dict:
        """
        Delete one or more assets.

        Args:
            asset_ids: List of asset IDs to delete
            project_id: Optional project ID the assets belong to

        Returns:
            Result object
        """
        params = {}
        if project_id:
            params["projectId"] = project_id

        return self.client.request(
            "DELETE", "/v1/co/assets", params=params, json=asset_ids
        )

    def set_metadata(
        self,
        asset_id: str,
        metadata: List[Dict],
        project_id: Optional[str] = None,
        delete: bool = False,
    ) -> Dict:
        """
        Set metadata for an asset.

        Args:
            asset_id: ID of the asset
            metadata: List of metadata objects to set
            project_id: Optional project ID
            delete: Whether to delete the specified metadata (instead of
                adding/updating)

        Returns:
            Updated asset object
        """
        params = {"assetId": asset_id, "delete": str(delete).lower()}
        if project_id:
            params["projectId"] = project_id

        return self.client.request(
            "PATCH", "/v1/co/assets/metadata", params=params, json=metadata
        )

    def get_by_path(self, file_path: str) -> List[Dict]:
        """
        Get all assets with a specific path.

        Args:
            file_path: The file path to search for

        Returns:
            List of matching asset objects
        """
        return self.client.request(
            "POST", "/v1/co/assets/getByPath", json=file_path
        )

    def get_unsynced_assets(self,
                            project_id: str,
                            limit: int = 500) -> List[Dict]:
        """
        Get all unsynced assets for a project.

        Args:
            project_id: ID of the project
            limit: Maximum number of results

        Returns:
            List of unsynced asset objects
        """
        params = {"limit": limit}
        return self.client.request(
            "GET", f"/v1/co/assets/unsynced/{project_id}", params=params
        )

    def toggle_synced(
        self,
        asset_ids: List[str],
        recursive: bool = False,
        force_sync: bool = False,
    ) -> List[Dict]:
        """
        Toggle sync status for assets.

        Args:
            asset_ids: List of asset IDs to toggle
            recursive: Whether to apply recursively to assets inside a folder
            force_sync: Whether to force assets to be synced (disable toggling)

        Returns:
            List of updated asset objects
        """
        params = {
            "recursive": str(recursive).lower(),
            "forceSync": str(force_sync).lower(),
        }
        return self.client.request(
            "POST", "/v1/co/assets/toggleSynced", params=params, json=asset_ids
        )
