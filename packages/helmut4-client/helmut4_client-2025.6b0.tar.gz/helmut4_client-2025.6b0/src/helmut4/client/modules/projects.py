"""
Projects module for Helmut4 client.
"""

from typing import BinaryIO, Dict, List, Optional

from ._base import BaseModule


class ProjectsModule(BaseModule):
    """Module for managing projects"""

    def search(
        self,
        search_filter: Optional[Dict] = None,
        limit: int = 500,
        page: int = 0,
    ) -> List[Dict]:
        """
        Search for projects based on a filter.

        Args:
            search_filter: Search filter criteria
            limit: Maximum number of results
            page: Page number for pagination

        Returns:
            List of matching project objects
        """
        params = {"limit": limit, "page": page}
        return self.client.request(
            "POST",
            "/v1/fx/projects/search",
            params=params,
            json=search_filter or {},
        )

    def get_by_id(self, project_id: str) -> Dict:
        """
        Get a project by ID.

        Args:
            project_id: The ID of the project

        Returns:
            Project object
        """
        return self.client.request("GET", f"/v1/fx/projects/{project_id}")

    def create(self, project_data: Dict) -> Dict:
        """
        Create a new project.

        Args:
            project_data: Project data

        Returns:
            Created project object
        """
        return self.client.request("POST", "/v1/fx/projects", json=project_data)

    def update(self, project_data: Dict) -> Dict:
        """
        Update an existing project.

        Args:
            project_data: Project data including the ID

        Returns:
            Updated project object
        """
        return self.client.request("PUT", "/v1/fx/projects", json=project_data)

    def delete(self, project_id: str, suppress_event: bool = False) -> Dict:
        """
        Delete a project.

        Args:
            project_id: ID of the project to delete
            suppress_event: Whether to suppress the UNLOCK_PROJECT event

        Returns:
            Result object
        """
        params = {}
        if suppress_event:
            params = {"suppressEvent": "true"}

        return self.client.request(
            "DELETE", f"/v1/fx/projects/{project_id}", params=params
        )

    def open(self, project_id: str) -> Dict:
        """
        Open a project.

        Args:
            project_id: ID of the project to open

        Returns:
            Project object
        """
        return self.client.request("GET", f"/v1/fx/projects/open/{project_id}")

    def duplicate(self, project_data: Dict) -> Dict:
        """
        Duplicate an existing project.

        Args:
            project_data: Source project data with modifications for the
                duplicate

        Returns:
            Created project object
        """
        return self.client.request(
            "POST", "/v1/fx/projects/duplicate", json=project_data
        )

    def download(self, project_id: str) -> bytes:
        """
        Download a project file.

        Args:
            project_id: ID of the project to download

        Returns:
            Binary project file content
        """
        return self.client.request(
            "GET", f"/v1/fx/projects/download/{project_id}"
        )

    def upload(self, project_id: str, file_content: BinaryIO) -> Dict:
        """
        Upload a project file.

        Args:
            project_id: ID of the project to update
            file_content: Binary content or file handle of the project file

        Returns:
            Updated project object
        """
        files = {"file": file_content}
        return self.client.request(
            "PUT", f"/v1/fx/projects/upload/{project_id}", files=files
        )

    def set_status(
        self,
        project_id: str,
        status: str,
        suppress_unlock_event: bool = False
    ) -> Dict:
        """
        Set a project's status.

        Args:
            project_id: ID of the project
            status: New status (e.g., "LOCKED", "UNLOCKED")
            suppress_unlock_event: Whether to suppress the AUTO_IMPORT event

        Returns:
            Updated project object
        """
        params = {}
        if suppress_unlock_event:
            params = {"suppressUnlockEvent": "true"}

        return self.client.request(
            "PUT",
            f"/v1/fx/projects/status/{project_id}",
            params=params,
            json={"status": status},
        )

    def get_templates(self, group: str, category: str) -> List[str]:
        """
        Get available templates for a group and category.

        Args:
            group: Project group
            category: Project category

        Returns:
            List of template names
        """
        return self.client.request(
            "GET", f"/v1/fx/templates/{group}/{category}"
        )

    def import_project(self, file_content: BinaryIO) -> str:
        """
        Import a project file.

        Args:
            file_content: Binary content or file handle of the project file

        Returns:
            Temporary path to the imported project
        """
        files = {"file": file_content}
        return self.client.request(
            "POST", "/v1/fx/projects/import", files=files
        )
