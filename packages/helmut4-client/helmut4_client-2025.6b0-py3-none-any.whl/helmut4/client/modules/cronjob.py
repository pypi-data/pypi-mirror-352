"""
Cronjob module for Helmut4 client.
"""

from typing import Dict, List

from ._base import BaseModule


class CronjobModule(BaseModule):
    """Module for managing cronjobs"""

    def get_all(self, limit: int = 500, page: int = 0) -> List[Dict]:
        """
        Get all cronjobs.

        Args:
            limit: Maximum number of results
            page: Page number for pagination

        Returns:
            List of cronjob objects
        """
        params = {"limit": limit, "page": page}
        return self.client.request("GET", "/v1/cronjob", params=params)

    def get_by_id(self, cronjob_id: str) -> Dict:
        """
        Get a cronjob by ID.

        Args:
            cronjob_id: The ID of the cronjob

        Returns:
            Cronjob object
        """
        return self.client.request("GET", f"/v1/cronjob/{cronjob_id}")

    def create(self, cronjob: Dict) -> Dict:
        """
        Create a new cronjob.

        Args:
            cronjob: Cronjob definition

        Returns:
            Created cronjob object
        """
        return self.client.request("POST", "/v1/cronjob", json=cronjob)

    def update(self, cronjob: Dict) -> Dict:
        """
        Update an existing cronjob.

        Args:
            cronjob: Cronjob data including the ID

        Returns:
            Updated cronjob object
        """
        return self.client.request("PUT", "/v1/cronjob", json=cronjob)

    def delete(self, cronjob_id: str) -> Dict:
        """
        Delete a cronjob.

        Args:
            cronjob_id: ID of the cronjob to delete

        Returns:
            Result object
        """
        return self.client.request("DELETE", f"/v1/cronjob/{cronjob_id}")

    def execute(self, cronjob_id: str, cron_triggered: bool = False) -> Dict:
        """
        Execute a cronjob immediately.

        Args:
            cronjob_id: ID of the cronjob to execute
            cron_triggered: Whether this execution is triggered by cron

        Returns:
            Execution result
        """
        params = {"cronTriggered": cron_triggered}
        return self.client.request(
            "GET", f"/v1/cronjob/{cronjob_id}", params=params
        )

    def explain_expression(self, cron_expression: str) -> List[str]:
        """
        Explain a cron expression by returning the next execution dates.

        Args:
            cron_expression: Cron expression to explain

        Returns:
            List of next execution dates
        """
        data = {"cronExpression": cron_expression}
        return self.client.request("POST", "/v1/cronjob/explain", json=data)
