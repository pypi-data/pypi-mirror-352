"""
Unit tests for JobsModule.
"""

from unittest.mock import Mock

import pytest

from helmut4.client.modules.jobs import JobsModule


class TestJobsModule:
    """Test JobsModule functionality."""

    @pytest.fixture
    def mock_client(self):
        """Mock client for testing."""
        client = Mock()
        client.request = Mock()
        return client

    @pytest.fixture
    def jobs_module(self, mock_client):
        """JobsModule instance for testing."""
        return JobsModule(mock_client)

    def test_get_all_default_params(
        self, jobs_module, mock_client, sample_job_data
    ):
        """Test get_all with default parameters."""
        mock_client.request.return_value = [sample_job_data]

        result = jobs_module.get_all()

        assert result == [sample_job_data]
        mock_client.request.assert_called_once_with(
            "GET", "/v1/io/jobs", params={
                "limit": 500,
                "page": 0
            }
        )

    def test_get_all_custom_params(self, jobs_module, mock_client):
        """Test get_all with custom parameters."""
        mock_client.request.return_value = []

        result = jobs_module.get_all(limit=100, page=2)

        assert result == []
        mock_client.request.assert_called_once_with(
            "GET", "/v1/io/jobs", params={
                "limit": 100,
                "page": 2
            }
        )

    def test_get_by_id(self, jobs_module, mock_client, sample_job_data):
        """Test get_by_id method."""
        mock_client.request.return_value = sample_job_data

        result = jobs_module.get_by_id("job123")

        assert result == sample_job_data
        mock_client.request.assert_called_once_with("GET", "/v1/io/jobs/job123")

    def test_search_default_params(
        self, jobs_module, mock_client, sample_job_data
    ):
        """Test search with default parameters."""
        mock_client.request.return_value = [sample_job_data]

        result = jobs_module.search()

        assert result == [sample_job_data]
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/io/jobs/search",
            params={
                "limit": 500,
                "page": 0
            },
            json={},
        )

    def test_search_with_filters(self, jobs_module, mock_client):
        """Test search with filter parameters."""
        mock_client.request.return_value = []

        search_filter = {
            "query": "render",
            "status": "running",
            "userId": "user123",
        }

        result = jobs_module.search(
            search_filter=search_filter,
            limit=50,
            page=1,
        )

        assert result == []
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/io/jobs/search",
            params={
                "limit": 50,
                "page": 1
            },
            json=search_filter,
        )

    def test_create(self, jobs_module, mock_client, sample_job_data):
        """Test create method."""
        job_data = {
            "name": "Test Render Job",
            "type": "render",
            "projectId": "proj123",
        }
        mock_client.request.return_value = sample_job_data

        result = jobs_module.create(job_data)

        assert result == sample_job_data
        mock_client.request.assert_called_once_with(
            "POST", "/v1/io/jobs", json=job_data
        )

    def test_update_default(self, jobs_module, mock_client, sample_job_data):
        """Test update method with default parameters."""
        update_data = {"id": "job123", "progress": 75, "status": "running"}
        mock_client.request.return_value = sample_job_data

        result = jobs_module.update(update_data)

        assert result == sample_job_data
        mock_client.request.assert_called_once_with(
            "PUT",
            "/v1/io/jobs",
            params={"postpone": "false"},
            json=update_data
        )

    def test_update_with_postpone(
        self, jobs_module, mock_client, sample_job_data
    ):
        """Test update method with postpone option."""
        update_data = {"id": "job123", "progress": 100, "status": "completed"}
        mock_client.request.return_value = sample_job_data

        result = jobs_module.update(update_data, postpone=True)

        assert result == sample_job_data
        mock_client.request.assert_called_once_with(
            "PUT", "/v1/io/jobs", params={"postpone": "true"}, json=update_data
        )

    def test_delete(self, jobs_module, mock_client):
        """Test delete method."""
        mock_client.request.return_value = "Job deleted successfully"

        result = jobs_module.delete("job123")

        assert result == "Job deleted successfully"
        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/io/jobs/job123"
        )

    def test_cancel(self, jobs_module, mock_client, sample_job_data):
        """Test cancel method."""
        job_data = {"id": "job123"}
        mock_client.request.return_value = sample_job_data

        result = jobs_module.cancel(job_data)

        assert result == sample_job_data
        mock_client.request.assert_called_once_with(
            "POST", "/v1/io/jobs/cancel", json=job_data
        )

    def test_update_logs(self, jobs_module, mock_client, sample_job_data):
        """Test update_logs method."""
        log_data = {
            "message": "Processing frame 100/200",
            "level": "info",
            "timestamp": "2023-01-01T12:00:00Z",
        }
        mock_client.request.return_value = sample_job_data

        result = jobs_module.update_logs("job123", log_data)

        assert result == sample_job_data
        mock_client.request.assert_called_once_with(
            "PUT", "/v1/io/jobs/logs/job123", json=log_data
        )

    def test_set_priority(self, jobs_module, mock_client, sample_job_data):
        """Test set_priority method."""
        job_data = {"id": "job123", "priority": 8}
        mock_client.request.return_value = sample_job_data

        result = jobs_module.set_priority("job123", job_data)

        assert result == sample_job_data
        mock_client.request.assert_called_once_with(
            "PUT", "/v1/io/jobs/priority/job123", json=job_data
        )

    def test_set_finish_date(self, jobs_module, mock_client, sample_job_data):
        """Test set_finish_date method."""
        mock_client.request.return_value = sample_job_data

        result = jobs_module.set_finish_date("job123")

        assert result == sample_job_data
        mock_client.request.assert_called_once_with(
            "PATCH", "/v1/io/jobs/job123/finish"
        )

    def test_request_processing(
        self, jobs_module, mock_client, sample_job_data
    ):
        """Test request_processing method."""
        mock_client.request.return_value = sample_job_data

        result = jobs_module.request_processing()

        assert result == sample_job_data
        mock_client.request.assert_called_once_with(
            "GET", "/v1/io/jobs/process"
        )

    def test_purge_old_jobs_default(self, jobs_module, mock_client):
        """Test purge_old_jobs with default parameters."""
        mock_client.request.return_value = {
            "deleted": 25,
            "message": "Jobs purged",
        }

        result = jobs_module.purge_old_jobs()

        assert result == {"deleted": 25, "message": "Jobs purged"}
        mock_client.request.assert_called_once_with("GET", "/v1/io/jobs/purge")

    def test_purge_old_jobs_no_params(self, jobs_module, mock_client):
        """Test purge_old_jobs method."""
        mock_client.request.return_value = {
            "deleted": 10,
            "message": "Jobs purged",
        }

        result = jobs_module.purge_old_jobs()

        assert result == {"deleted": 10, "message": "Jobs purged"}
        mock_client.request.assert_called_once_with("GET", "/v1/io/jobs/purge")
