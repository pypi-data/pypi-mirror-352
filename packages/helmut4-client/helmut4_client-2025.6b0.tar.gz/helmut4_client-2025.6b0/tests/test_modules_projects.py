"""
Unit tests for ProjectsModule.
"""

from unittest.mock import Mock

import pytest

from helmut4.client.modules.projects import ProjectsModule


class TestProjectsModule:
    """Test ProjectsModule functionality."""

    @pytest.fixture
    def mock_client(self):
        """Mock client for testing."""
        client = Mock()
        client.request = Mock()
        return client

    @pytest.fixture
    def projects_module(self, mock_client):
        """ProjectsModule instance for testing."""
        return ProjectsModule(mock_client)

    def test_search_default_params(
        self, projects_module, mock_client, sample_project_data
    ):
        """Test search with default parameters."""
        mock_client.request.return_value = [sample_project_data]

        result = projects_module.search()

        assert result == [sample_project_data]
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/fx/projects/search",
            params={
                "limit": 500,
                "page": 0
            },
            json={},
        )

    def test_search_custom_params(self, projects_module, mock_client):
        """Test search with custom parameters."""
        mock_client.request.return_value = []

        search_filter = {"query": "test", "status": "LOCKED"}

        result = projects_module.search(
            search_filter=search_filter, limit=100, page=1
        )

        assert result == []
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/fx/projects/search",
            params={
                "limit": 100,
                "page": 1
            },
            json=search_filter,
        )

    def test_get_by_id(self, projects_module, mock_client, sample_project_data):
        """Test get_by_id method."""
        mock_client.request.return_value = sample_project_data

        result = projects_module.get_by_id("proj123")

        assert result == sample_project_data
        mock_client.request.assert_called_once_with(
            "GET", "/v1/fx/projects/proj123"
        )

    def test_create(self, projects_module, mock_client, sample_project_data):
        """Test create method."""
        project_data = {
            "name": "New Project",
            "description": "A new test project",
        }
        mock_client.request.return_value = sample_project_data

        result = projects_module.create(project_data)

        assert result == sample_project_data
        mock_client.request.assert_called_once_with(
            "POST", "/v1/fx/projects", json=project_data
        )

    def test_update(self, projects_module, mock_client, sample_project_data):
        """Test update method."""
        update_data = {"id": "proj123", "description": "Updated description"}
        mock_client.request.return_value = sample_project_data

        result = projects_module.update(update_data)

        assert result == sample_project_data
        mock_client.request.assert_called_once_with(
            "PUT", "/v1/fx/projects", json=update_data
        )

    def test_delete_default(self, projects_module, mock_client):
        """Test delete method with default parameters."""
        mock_client.request.return_value = "Project deleted"

        result = projects_module.delete("proj123")

        assert result == "Project deleted"
        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/fx/projects/proj123", params={}
        )

    def test_delete_suppress_event(self, projects_module, mock_client):
        """Test delete method with suppressed event."""
        mock_client.request.return_value = "Project deleted"

        result = projects_module.delete("proj123", suppress_event=True)

        assert result == "Project deleted"
        mock_client.request.assert_called_once_with(
            "DELETE",
            "/v1/fx/projects/proj123",
            params={"suppressEvent": "true"},
        )

    def test_open(self, projects_module, mock_client, sample_project_data):
        """Test open method."""
        mock_client.request.return_value = sample_project_data

        result = projects_module.open("proj123")

        assert result == sample_project_data
        mock_client.request.assert_called_once_with(
            "GET", "/v1/fx/projects/open/proj123"
        )

    def test_duplicate(self, projects_module, mock_client, sample_project_data):
        """Test duplicate method."""
        duplicate_data = {"id": "proj123", "name": "Copied Project"}
        mock_client.request.return_value = sample_project_data

        result = projects_module.duplicate(duplicate_data)

        assert result == sample_project_data
        mock_client.request.assert_called_once_with(
            "POST", "/v1/fx/projects/duplicate", json=duplicate_data
        )

    def test_download(self, projects_module, mock_client):
        """Test download method."""
        mock_client.request.return_value = b"project file data"

        result = projects_module.download("proj123")

        assert result == b"project file data"
        mock_client.request.assert_called_once_with(
            "GET", "/v1/fx/projects/download/proj123"
        )

    def test_upload(self, projects_module, mock_client, sample_project_data):
        """Test upload method."""
        file_data = b"project file content"
        mock_client.request.return_value = sample_project_data

        result = projects_module.upload("proj123", file_data)

        assert result == sample_project_data
        mock_client.request.assert_called_once_with(
            "PUT", "/v1/fx/projects/upload/proj123", files={"file": file_data}
        )

    def test_set_status_locked(
        self, projects_module, mock_client, sample_project_data
    ):
        """Test set_status method to LOCKED."""
        mock_client.request.return_value = sample_project_data

        result = projects_module.set_status("proj123", "LOCKED")

        assert result == sample_project_data
        mock_client.request.assert_called_once_with(
            "PUT",
            "/v1/fx/projects/status/proj123",
            params={},
            json={"status": "LOCKED"},
        )

    def test_set_status_unlocked(
        self, projects_module, mock_client, sample_project_data
    ):
        """Test set_status method to UNLOCKED."""
        mock_client.request.return_value = sample_project_data

        result = projects_module.set_status("proj123", "UNLOCKED")

        assert result == sample_project_data
        mock_client.request.assert_called_once_with(
            "PUT",
            "/v1/fx/projects/status/proj123",
            params={},
            json={"status": "UNLOCKED"},
        )

    def test_get_templates(self, projects_module, mock_client):
        """Test get_templates method."""
        templates = ["Basic Template", "Advanced Template"]
        mock_client.request.return_value = templates

        result = projects_module.get_templates("testgroup", "video")

        assert result == templates
        mock_client.request.assert_called_once_with(
            "GET", "/v1/fx/templates/testgroup/video"
        )

    def test_import_project(self, projects_module, mock_client):
        """Test import_project method."""
        file_data = b"project import data"
        mock_client.request.return_value = "/tmp/imported_project_path"

        result = projects_module.import_project(file_data)

        assert result == "/tmp/imported_project_path"
        mock_client.request.assert_called_once_with(
            "POST", "/v1/fx/projects/import", files={"file": file_data}
        )
