"""
Unit tests for StreamsModule.
"""

from unittest.mock import Mock

import pytest

from helmut4.client.modules.streams import StreamsModule


class TestStreamsModule:
    """Test StreamsModule functionality."""

    @pytest.fixture
    def mock_client(self):
        """Mock client for testing."""
        client = Mock()
        client.request = Mock()
        return client

    @pytest.fixture
    def streams_module(self, mock_client):
        """StreamsModule instance for testing."""
        return StreamsModule(mock_client)

    def test_get_all(self, streams_module, mock_client, sample_stream_data):
        """Test get_all method."""
        mock_client.request.return_value = [sample_stream_data]

        result = streams_module.get_all()

        assert result == [sample_stream_data]
        mock_client.request.assert_called_once_with("GET", "/v1/streams")

    def test_get_by_id(self, streams_module, mock_client, sample_stream_data):
        """Test get_by_id method."""
        mock_client.request.return_value = sample_stream_data

        result = streams_module.get_by_id("stream123")

        assert result == sample_stream_data
        mock_client.request.assert_called_once_with(
            "GET", "/v1/streams/id/stream123"
        )

    def test_get_by_event(
        self, streams_module, mock_client, sample_stream_data
    ):
        """Test get_by_event method."""
        mock_client.request.return_value = [sample_stream_data]

        result = streams_module.get_by_event("onAssetCreate")

        assert result == [sample_stream_data]
        mock_client.request.assert_called_once_with(
            "GET", "/v1/streams/event/onAssetCreate"
        )

    def test_get_by_tags(self, streams_module, mock_client, sample_stream_data):
        """Test get_by_tags method."""
        mock_client.request.return_value = [sample_stream_data]

        result = streams_module.get_by_tags(["automation", "workflow"])

        assert result == [sample_stream_data]
        mock_client.request.assert_called_once_with(
            "GET", "/v1/streams/automation,workflow", params={"design": "true"}
        )

    def test_create(self, streams_module, mock_client, sample_stream_data):
        """Test create method."""
        stream_data = {
            "name": "New Stream",
            "event": "onAssetCreate",
            "enabled": True,
            "conditions": [],
            "actions": [],
        }
        mock_client.request.return_value = sample_stream_data

        result = streams_module.create(stream_data)

        assert result == sample_stream_data
        mock_client.request.assert_called_once_with(
            "POST", "/v1/streams", json=stream_data
        )

    def test_update(self, streams_module, mock_client, sample_stream_data):
        """Test update method."""
        update_data = {
            "id": "stream123",
            "enabled": False,
            "name": "Updated Stream",
        }
        mock_client.request.return_value = sample_stream_data

        result = streams_module.update(update_data)

        assert result == sample_stream_data
        mock_client.request.assert_called_once_with(
            "PUT", "/v1/streams", json=update_data
        )

    def test_delete(self, streams_module, mock_client):
        """Test delete method."""
        mock_client.request.return_value = "Stream deleted successfully"

        result = streams_module.delete("stream123")

        assert result == "Stream deleted successfully"
        mock_client.request.assert_called_once_with(
            "DELETE", "/v1/streams/stream123"
        )

    def test_update_status_enable(
        self, streams_module, mock_client, sample_stream_data
    ):
        """Test update_status to enable stream."""
        mock_client.request.return_value = sample_stream_data

        result = streams_module.update_status("stream123", True)

        assert result == sample_stream_data
        mock_client.request.assert_called_once_with(
            "PUT", "/v1/streams/status/stream123/true"
        )

    def test_update_status_disable(
        self, streams_module, mock_client, sample_stream_data
    ):
        """Test update_status to disable stream."""
        mock_client.request.return_value = sample_stream_data

        result = streams_module.update_status("stream123", False)

        assert result == sample_stream_data
        mock_client.request.assert_called_once_with(
            "PUT", "/v1/streams/status/stream123/false"
        )

    def test_execute(self, streams_module, mock_client):
        """Test execute method."""
        content_package = {"assetId": "asset123", "projectId": "proj123"}
        mock_client.request.return_value = {"success": True, "executed": True}

        result = streams_module.execute("onAssetCreate", "FX", content_package)

        assert result == {"success": True, "executed": True}
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/streams/execute/onAssetCreate/FX",
            json=content_package
        )

    def test_execute_custom(self, streams_module, mock_client):
        """Test execute_custom method."""
        mock_client.request.return_value = {"success": True}

        result = streams_module.execute_custom("stream123")

        assert result == {"success": True}
        mock_client.request.assert_called_once_with(
            "GET", "/v1/streams/execute/custom/stream123"
        )

    def test_test_stream(self, streams_module, mock_client):
        """Test test_stream method."""
        stream_data = {
            "id": "stream123",
            "name": "Test Stream",
            "event": "onAssetCreate",
            "actions": [],
        }
        mock_client.request.return_value = "Test completed successfully"

        result = streams_module.test_stream(stream_data)

        assert result == "Test completed successfully"
        mock_client.request.assert_called_once_with(
            "POST", "/v1/streams/do/test", json=stream_data
        )

    def test_test_path(self, streams_module, mock_client):
        """Test test_path method."""
        mock_client.request.return_value = "/resolved/path/file.mp4"

        result = streams_module.test_path("/original/path/{asset.name}")

        assert result == "/resolved/path/file.mp4"
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/streams/do/test/path",
            params={},
            json="/original/path/{asset.name}",
        )

    def test_export(self, streams_module, mock_client):
        """Test export method."""
        mock_client.request.return_value = b"exported streams data"

        result = streams_module.export(["stream123", "stream456"])

        assert result == b"exported streams data"
        mock_client.request.assert_called_once_with(
            "GET", "/v1/streams/export/stream123,stream456"
        )

    def test_import_streams_default(self, streams_module, mock_client):
        """Test import_streams with default parameters."""
        file_data = b"streams import data"
        mock_client.request.return_value = {"imported": 5, "skipped": 1}

        result = streams_module.import_streams(file_data)

        assert result == {"imported": 5, "skipped": 1}
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/streams/import",
            params={
                "conflict": "RENAME",
                "purge": "false"
            },
            files={"file": file_data},
        )

    def test_import_streams_with_overwrite(self, streams_module, mock_client):
        """Test import_streams with overwrite option."""
        file_data = b"streams import data"
        mock_client.request.return_value = {"imported": 3, "overwritten": 2}

        result = streams_module.import_streams(
            file_data, conflict="OVERWRITE", purge=True
        )

        assert result == {"imported": 3, "overwritten": 2}
        mock_client.request.assert_called_once_with(
            "POST",
            "/v1/streams/import",
            params={
                "conflict": "OVERWRITE",
                "purge": "true"
            },
            files={"file": file_data},
        )

    def test_get_events(self, streams_module, mock_client):
        """Test get_events method."""
        events = [
            {
                "name": "onAssetCreate",
                "description": "When asset is created"
            },
            {
                "name": "onAssetUpdate",
                "description": "When asset is updated"
            },
        ]
        mock_client.request.return_value = events

        result = streams_module.get_events()

        assert result == events
        mock_client.request.assert_called_once_with(
            "GET", "/v1/streams/list/events"
        )

    def test_get_events_by_tags(self, streams_module, mock_client):
        """Test get_events_by_tags method."""
        events = [{"name": "onAssetCreate", "tags": ["asset", "create"]}]
        mock_client.request.return_value = events

        result = streams_module.get_events_by_tags(["asset", "create"])

        assert result == events
        mock_client.request.assert_called_once_with(
            "GET", "/v1/streams/list/events/asset,create"
        )

    def test_resolve_string(self, streams_module, mock_client):
        """Test resolve_string method."""
        resolve_data = {
            "string": "Asset {asset.name} created",
            "context": {
                "asset": {
                    "name": "test.mp4"
                }
            },
        }
        mock_client.request.return_value = {
            "resolved": "Asset test.mp4 created"
        }

        result = streams_module.resolve_string(resolve_data)

        assert result == {"resolved": "Asset test.mp4 created"}
        mock_client.request.assert_called_once_with(
            "POST", "/v1/streams/string/resolve", json=resolve_data
        )

    def test_get_file_contents(self, streams_module, mock_client):
        """Test get_file_contents method."""
        file_chooser_data = {"path": "/projects/test", "filter": "*.mp4"}
        mock_client.request.return_value = {
            "files": ["file1.mp4", "file2.avi"],
            "folders": ["subfolder1", "subfolder2"],
        }

        result = streams_module.get_file_contents(file_chooser_data)

        assert result == {
            "files": ["file1.mp4", "file2.avi"],
            "folders": ["subfolder1", "subfolder2"],
        }
        mock_client.request.assert_called_once_with(
            "POST", "/v1/streams/fileChooser", json=file_chooser_data
        )

    def test_get_actions(self, streams_module, mock_client):
        """Test get_actions method."""
        actions = [
            {
                "id": "action1",
                "name": "Log Message"
            },
            {
                "id": "action2",
                "name": "Send Email"
            },
        ]
        mock_client.request.return_value = actions

        result = streams_module.get_actions()

        assert result == actions
        mock_client.request.assert_called_once_with(
            "GET", "/v1/streams/list/actions"
        )

    def test_get_conditions(self, streams_module, mock_client):
        """Test get_conditions method."""
        conditions = [
            {
                "id": "cond1",
                "name": "File Extension"
            },
            {
                "id": "cond2",
                "name": "File Size"
            },
        ]
        mock_client.request.return_value = conditions

        result = streams_module.get_conditions()

        assert result == conditions
        mock_client.request.assert_called_once_with(
            "GET", "/v1/streams/list/conditions"
        )

    def test_get_outputs(self, streams_module, mock_client):
        """Test get_outputs method."""
        outputs = [
            {
                "id": "out1",
                "name": "File Output"
            },
            {
                "id": "out2",
                "name": "Database Output"
            },
        ]
        mock_client.request.return_value = outputs

        result = streams_module.get_outputs()

        assert result == outputs
        mock_client.request.assert_called_once_with(
            "GET", "/v1/streams/list/outputs"
        )

    def test_get_wildcards(self, streams_module, mock_client):
        """Test get_wildcards method."""
        wildcards = [
            {
                "id": "wild1",
                "name": "{asset.name}"
            },
            {
                "id": "wild2",
                "name": "{project.id}"
            },
        ]
        mock_client.request.return_value = wildcards

        result = streams_module.get_wildcards()

        assert result == wildcards
        mock_client.request.assert_called_once_with(
            "GET", "/v1/streams/list/wildcards"
        )

    def test_resolve_metadata(self, streams_module, mock_client):
        """Test resolve_metadata method."""
        metadata_package = {
            "metadata": [{
                "key": "title",
                "value": "{asset.name}"
            }],
            "context": {
                "asset": {
                    "name": "test.mp4"
                }
            },
        }
        mock_client.request.return_value = [{
            "key": "title",
            "value": "test.mp4"
        }]

        result = streams_module.resolve_metadata(metadata_package)

        assert result == [{"key": "title", "value": "test.mp4"}]
        mock_client.request.assert_called_once_with(
            "POST", "/v1/streams/metadata/resolve", json=metadata_package
        )
