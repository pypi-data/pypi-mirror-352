"""
Unit tests for AssetsModule.
"""

from unittest.mock import Mock

import pytest

from helmut4.client.modules.assets import AssetsModule


class TestAssetsModule:
    """Test AssetsModule functionality."""

    @pytest.fixture
    def mock_client(self):
        """Mock client for testing."""
        client = Mock()
        client.request = Mock()
        return client

    @pytest.fixture
    def assets_module(self, mock_client):
        """AssetsModule instance for testing."""
        return AssetsModule(mock_client)

    def test_search_default_params(
        self, assets_module, mock_client, sample_asset_data
    ):
        """Test search with default parameters."""
        mock_client.request.return_value = [sample_asset_data]

        result = assets_module.search()

        assert result == [sample_asset_data]
        mock_client.request.assert_called_once_with(
            "POST", "/v1/co/search", params={
                "limit": 500,
                "page": 0
            }, json={}
        )

    def test_search_with_filters(self, assets_module, mock_client):
        """Test search with filter parameters."""
        mock_client.request.return_value = []

        search_filter = {"type": "video", "name": "test.mp4"}
        result = assets_module.search(
            search_filter=search_filter,
            project_id="proj123",
            limit=100,
            page=1
        )

        assert result == []
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/co/search",
            params={
                "limit": 100,
                "page": 1,
                "projectId": "proj123"
            },
            json=search_filter,
        )

    def test_get_by_id(self, assets_module, mock_client, sample_asset_data):
        """Test get_by_id method."""
        mock_client.request.return_value = sample_asset_data

        result = assets_module.get_by_id("asset123")

        assert result == sample_asset_data
        mock_client.request.assert_called_once_with(
            "GET", "/v1/co/assets", params={"assetId": "asset123"}
        )

    def test_get_by_project_id_default(
        self, assets_module, mock_client, sample_asset_data
    ):
        """Test get_by_project_id method."""
        mock_client.request.return_value = [sample_asset_data]

        result = assets_module.get_by_project_id("proj123")

        assert result == [sample_asset_data]
        mock_client.request.assert_called_once_with(
            "GET", "/v1/co/assets/proj123"
        )

    def test_get_by_project_id_empty_result(self, assets_module, mock_client):
        """Test get_by_project_id with empty result."""
        mock_client.request.return_value = []

        result = assets_module.get_by_project_id("proj123")

        assert result == []
        mock_client.request.assert_called_once_with(
            "GET", "/v1/co/assets/proj123"
        )

    def test_create_default(
        self, assets_module, mock_client, sample_asset_data
    ):
        """Test create method with default parameters."""
        asset_data = {
            "name": "new_asset.mp4",
            "path": "/projects/test/new_asset.mp4",
            "projectId": "proj123",
        }
        mock_client.request.return_value = sample_asset_data

        result = assets_module.create(asset_data)

        assert result == sample_asset_data
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/co/assets",
            params={"createBinStructure": "true"},
            json=asset_data,
        )

    def test_create_without_bin_structure(
        self, assets_module, mock_client, sample_asset_data
    ):
        """Test create method without bin structure creation."""
        asset_data = {
            "name": "new_asset.mp4",
            "path": "/projects/test/new_asset.mp4",
        }
        mock_client.request.return_value = sample_asset_data

        result = assets_module.create(asset_data, create_bin_structure=False)

        assert result == sample_asset_data
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/co/assets",
            params={"createBinStructure": "false"},
            json=asset_data,
        )

    def test_update(self, assets_module, mock_client, sample_asset_data):
        """Test update method."""
        update_data = {"id": "asset123", "name": "updated_asset.mp4"}
        mock_client.request.return_value = sample_asset_data

        result = assets_module.update(update_data)

        assert result == sample_asset_data
        mock_client.request.assert_called_once_with(
            "PUT", "/v1/co/assets", json=update_data
        )

    def test_patch(self, assets_module, mock_client, sample_asset_data):
        """Test patch method."""
        patch_data = {"id": "asset123", "metadata": {"title": "Updated Title"}}
        mock_client.request.return_value = sample_asset_data

        result = assets_module.patch(patch_data)

        assert result == sample_asset_data
        mock_client.request.assert_called_once_with(
            "PATCH", "/v1/co/assets", json=patch_data
        )

    def test_delete(self, assets_module, mock_client):
        """Test delete method."""
        asset_ids = ["asset123", "asset456"]
        mock_client.request.return_value = {"deleted": 2}

        result = assets_module.delete(asset_ids)

        assert result == {"deleted": 2}
        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/co/assets", params={}, json=asset_ids
        )

    def test_set_metadata(self, assets_module, mock_client, sample_asset_data):
        """Test set_metadata method."""
        metadata = [{"name": "title", "value": "New Title"}]
        mock_client.request.return_value = sample_asset_data

        result = assets_module.set_metadata("asset123", metadata)

        assert result == sample_asset_data
        mock_client.request.assert_called_once_with(
            "PATCH",
            "/v1/co/assets/metadata",
            params={
                "assetId": "asset123",
                "delete": "false"
            },
            json=metadata,
        )

    def test_get_unsynced_assets(
        self, assets_module, mock_client, sample_asset_data
    ):
        """Test get_unsynced_assets method."""
        mock_client.request.return_value = [sample_asset_data]

        result = assets_module.get_unsynced_assets("proj123")

        assert result == [sample_asset_data]
        mock_client.request.assert_called_once_with(
            "GET", "/v1/co/assets/unsynced/proj123", params={"limit": 500}
        )

    def test_get_by_path(self, assets_module, mock_client, sample_asset_data):
        """Test get_by_path method."""
        mock_client.request.return_value = [sample_asset_data]

        result = assets_module.get_by_path("/projects/test/asset.mp4")

        assert result == [sample_asset_data]
        mock_client.request.assert_called_once_with(
            "POST", "/v1/co/assets/getByPath", json="/projects/test/asset.mp4"
        )
