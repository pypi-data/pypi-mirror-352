"""
Jobs module for Helmut4 client.
"""

from typing import Dict, List, Optional

from ._base import BaseModule


class JobsModule(BaseModule):
    """Module for managing jobs"""

    def get_all(self, limit: int = 500, page: int = 0) -> List[Dict]:
        """
        Get all jobs.

        Args:
            limit: Maximum number of results
            page: Page number for pagination

        Returns:
            List of job objects
        """
        params = {"limit": limit, "page": page}
        return self.client.request("GET", "/v1/io/jobs", params=params)

    def get_by_id(self, job_id: str) -> Dict:
        """
        Get a job by ID.

        Args:
            job_id: The ID of the job

        Returns:
            Job object
        """
        return self.client.request("GET", f"/v1/io/jobs/{job_id}")

    def create(self, job_data: Dict) -> Dict:
        """
        Create a new job.

        Args:
            job_data: Job data

        Returns:
            Created job object
        """
        return self.client.request("POST", "/v1/io/jobs", json=job_data)

    def update(self, job_data: Dict, postpone: bool = False) -> Dict:
        """
        Update a job's progress and status.

        Args:
            job_data: Job data including the ID
            postpone: Whether to postpone the job

        Returns:
            Updated job object
        """
        params = {"postpone": str(postpone).lower()}
        return self.client.request(
            "PUT", "/v1/io/jobs", params=params, json=job_data
        )

    def delete(self, job_id: str) -> Dict:
        """
        Delete a job.

        Args:
            job_id: ID of the job to delete

        Returns:
            Result object
        """
        return self.client.request("DELETE", f"/v1/io/jobs/{job_id}")

    def cancel(self, job_data: Dict) -> Dict:
        """
        Cancel a running job.

        Args:
            job_data: Job data including at minimum the ID

        Returns:
            Result object
        """
        return self.client.request("POST", "/v1/io/jobs/cancel", json=job_data)

    def search(
        self,
        search_filter: Optional[Dict] = None,
        limit: int = 500,
        page: int = 0,
    ) -> List[Dict]:
        """
        Search for jobs based on a filter.

        Args:
            search_filter: Search filter criteria
            limit: Maximum number of results
            page: Page number for pagination

        Returns:
            List of matching job objects
        """
        params = {"limit": limit, "page": page}
        return self.client.request(
            "POST",
            "/v1/io/jobs/search",
            params=params,
            json=search_filter or {},
        )

    def update_logs(self, job_id: str, logs_data: Dict) -> Dict:
        """
        Update a job's log entries.

        Args:
            job_id: ID of the job
            logs_data: Log data to update

        Returns:
            Updated job object
        """
        return self.client.request(
            "PUT", f"/v1/io/jobs/logs/{job_id}", json=logs_data
        )

    def set_priority(self, job_id: str, job_data: Dict) -> Dict:
        """
        Set a job's priority.

        Args:
            job_id: ID of the job
            job_data: Job data with updated priority

        Returns:
            Updated job object
        """
        return self.client.request(
            "PUT", f"/v1/io/jobs/priority/{job_id}", json=job_data
        )

    def set_finish_date(self, job_id: str) -> Dict:
        """
        Set a job's finish date to now.

        Args:
            job_id: ID of the job

        Returns:
            Updated job object
        """
        return self.client.request("PATCH", f"/v1/io/jobs/{job_id}/finish")

    def request_processing(self) -> Dict:
        """
        Request a new render job to be processed.

        Returns:
            Result object
        """
        return self.client.request("GET", "/v1/io/jobs/process")

    def purge_old_jobs(self) -> Dict:
        """
        Purge old jobs based on system settings.

        Returns:
            Result object
        """
        return self.client.request("GET", "/v1/io/jobs/purge")
