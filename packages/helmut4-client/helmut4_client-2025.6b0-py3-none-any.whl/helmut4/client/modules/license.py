"""
License module for Helmut4 client.
"""

from typing import Dict

from ._base import BaseModule


class LicenseModule(BaseModule):
    """Module for managing licenses"""

    def get_all(self) -> Dict:
        """
        Get all licenses.

        Returns:
            License object(s)
        """
        return self.client.request("GET", "/v1/license")

    def add(self, jwt_token: str) -> Dict:
        """
        Add a new license.

        Args:
            jwt_token: JWT license token

        Returns:
            Created license object
        """
        return self.client.request(
            "POST", "/v1/license", json={"token": jwt_token}
        )

    def delete(self) -> str:
        """
        Delete the current license.

        Returns:
            Success message
        """
        return self.client.request("DELETE", "/v1/license")

    def get_hardware_id(self) -> Dict:
        """
        Get the hardware ID of the system.

        Returns:
            Hardware ID object
        """
        return self.client.request("GET", "/v1/license/hardwareId")

    def get_client_version(self) -> Dict:
        """
        Get the client version.

        Returns:
            Client version object
        """
        return self.client.request("GET", "/v1/license/client/version")

    def get_helmut_version(self) -> Dict:
        """
        Get the Helmut version.

        Returns:
            Helmut version object
        """
        return self.client.request("GET", "/v1/license/helmut/version")
