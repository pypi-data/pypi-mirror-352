"""
Streams module for Helmut4 client.
"""

from typing import BinaryIO, Dict, List, Optional

from ._base import BaseModule


class StreamsModule(BaseModule):
    """Module for managing streams (workflows)"""

    def get_all(self) -> List[Dict]:
        """
        Get all streams.

        Returns:
            List of stream objects
        """
        return self.client.request("GET", "/v1/streams")

    def get_by_id(self, stream_id: str) -> Dict:
        """
        Get a stream by ID.

        Args:
            stream_id: The ID of the stream

        Returns:
            Stream object
        """
        return self.client.request("GET", f"/v1/streams/id/{stream_id}")

    def get_by_event(self, event: str) -> List[Dict]:
        """
        Get streams for a specific event.

        Args:
            event: The event name (e.g., "CREATE_PROJECT")

        Returns:
            List of stream objects
        """
        return self.client.request("GET", f"/v1/streams/event/{event}")

    def get_by_tags(self, tags: List[str], design: bool = True) -> List[Dict]:
        """
        Get streams matching specified tags.

        Args:
            tags: List of tags to filter by
            design: Whether to include design information

        Returns:
            List of matching stream objects
        """
        tags_str = ",".join(tags)
        params = {"design": str(design).lower()}
        return self.client.request(
            "GET", f"/v1/streams/{tags_str}", params=params
        )

    def create(self, stream_data: Dict) -> Dict:
        """
        Create a new stream.

        Args:
            stream_data: Stream definition

        Returns:
            Created stream object
        """
        return self.client.request("POST", "/v1/streams", json=stream_data)

    def update(self, stream_data: Dict) -> Dict:
        """
        Update an existing stream.

        Args:
            stream_data: Stream data including the ID

        Returns:
            Updated stream object
        """
        return self.client.request("PUT", "/v1/streams", json=stream_data)

    def delete(self, stream_id: str) -> Dict:
        """
        Delete a stream.

        Args:
            stream_id: ID of the stream to delete

        Returns:
            Result object
        """
        return self.client.request("DELETE", f"/v1/streams/{stream_id}")

    def update_status(self, stream_id: str, status: bool) -> Dict:
        """
        Update a stream's enabled/disabled status.

        Args:
            stream_id: ID of the stream
            status: True for enabled, False for disabled

        Returns:
            Updated stream object
        """
        return self.client.request(
            "PUT", f"/v1/streams/status/{stream_id}/{str(status).lower()}"
        )

    def execute(
        self, stream_event: str, endpoint: str, content_package: Dict
    ) -> Dict:
        """
        Execute a stream.

        Args:
            stream_event: Event type triggering the stream
            endpoint: Target endpoint (e.g., "FX")
            content_package: Stream content package with execution data

        Returns:
            Stream execution result
        """
        return self.client.request(
            "POST",
            f"/v1/streams/execute/{stream_event}/{endpoint}",
            json=content_package,
        )

    def execute_custom(
        self, stream_id: str, project_id: Optional[str] = None
    ) -> Dict:
        """
        Execute a custom stream.

        Args:
            stream_id: ID of the stream to execute
            project_id: Optional project ID

        Returns:
            Execution result
        """
        if project_id:
            endpoint = f"/v1/fx/projects/execute/custom/{project_id}/{stream_id}"  # pylint: disable=line-too-long
        else:
            endpoint = f"/v1/streams/execute/custom/{stream_id}"

        return self.client.request("GET", endpoint)

    def test_stream(self, stream_data: Dict) -> str:
        """
        Test a stream without executing it.

        Args:
            stream_data: Stream definition to test

        Returns:
            Test result log
        """
        return self.client.request(
            "POST", "/v1/streams/do/test", json=stream_data
        )

    def test_path(self, path: str, os: Optional[str] = None) -> str:
        """
        Test path resolution.

        Args:
            path: Path to test
            os: Optional OS to force for resolution (WINDOWS, UNIX, AUTO)

        Returns:
            Resolved path
        """
        params = {}
        if os:
            params["os"] = os

        return self.client.request(
            "POST", "/v1/streams/do/test/path", params=params, json=path
        )

    def export(self, stream_ids: List[str]) -> bytes:
        """
        Export streams.

        Args:
            stream_ids: List of stream IDs to export

        Returns:
            Binary export file content
        """
        return self.client.request(
            "GET", f"/v1/streams/export/{','.join(stream_ids)}"
        )

    def import_streams(
        self,
        file_content: BinaryIO,
        conflict: str = "RENAME",
        purge: bool = False,
    ) -> Dict:
        """
        Import streams.

        Args:
            file_content: Binary content or file handle of the stream export
                file
            conflict: How to handle conflicts (RENAME, SKIP, OVERWRITE)
            purge: Whether to delete all existing streams first

        Returns:
            Import result
        """
        params = {"conflict": conflict, "purge": str(purge).lower()}
        files = {"file": file_content}
        return self.client.request(
            "POST", "/v1/streams/import", params=params, files=files
        )

    def get_events(self) -> List[str]:
        """
        Get all available stream events.

        Returns:
            List of event names
        """
        return self.client.request("GET", "/v1/streams/list/events")

    def get_events_by_tags(self, tags: List[str]) -> List[str]:
        """
        Get stream events filtered by tags.

        Args:
            tags: List of tags to filter by

        Returns:
            List of event names
        """
        return self.client.request(
            "GET", f"/v1/streams/list/events/{','.join(tags)}"
        )

    def get_actions(self) -> List[Dict]:
        """
        Get all available stream actions.

        Returns:
            List of action definitions
        """
        return self.client.request("GET", "/v1/streams/list/actions")

    def get_conditions(self) -> List[Dict]:
        """
        Get all available stream conditions.

        Returns:
            List of condition definitions
        """
        return self.client.request("GET", "/v1/streams/list/conditions")

    def get_outputs(self) -> List[Dict]:
        """
        Get all available stream outputs.

        Returns:
            List of output definitions
        """
        return self.client.request("GET", "/v1/streams/list/outputs")

    def get_wildcards(self) -> List[Dict]:
        """
        Get all available stream wildcards.

        Returns:
            List of wildcard definitions
        """
        return self.client.request("GET", "/v1/streams/list/wildcards")

    def resolve_string(self, resolve_package: Dict) -> Dict:
        """
        Resolve a string using the stream engine.

        Args:
            resolve_package: String resolve package with data

        Returns:
            Resolved string package
        """
        return self.client.request(
            "POST", "/v1/streams/string/resolve", json=resolve_package
        )

    def resolve_metadata(self, metadata_package: Dict) -> List[Dict]:
        """
        Resolve metadata using the stream engine.

        Args:
            metadata_package: Metadata resolve package with data

        Returns:
            List of resolved metadata objects
        """
        return self.client.request(
            "POST", "/v1/streams/metadata/resolve", json=metadata_package
        )

    def get_file_contents(self, file_chooser_data: Dict) -> Dict:
        """
        Get the contents of a folder.

        Args:
            file_chooser_data: File chooser configuration

        Returns:
            File chooser result with folder contents
        """
        return self.client.request(
            "POST", "/v1/streams/fileChooser", json=file_chooser_data
        )
