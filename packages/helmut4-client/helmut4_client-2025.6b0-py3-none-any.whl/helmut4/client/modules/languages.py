"""
Languages module for Helmut4 client.
"""

from typing import Dict, List

from ._base import BaseModule


class LanguagesModule(BaseModule):
    """Module for managing languages"""

    def get_all(self) -> List[Dict]:
        """
        Get all languages.

        Returns:
            List of language objects
        """
        return self.client.request("GET", "/v1/languages")

    def create(self, language: Dict) -> Dict:
        """
        Create a new language.

        Args:
            language: Language definition

        Returns:
            Created language object
        """
        return self.client.request("POST", "/v1/languages", json=language)

    def update(self, language: Dict) -> Dict:
        """
        Update an existing language.

        Args:
            language: Language data including the ID

        Returns:
            Updated language object
        """
        return self.client.request("PUT", "/v1/languages", json=language)

    def delete(self, language_id: str) -> str:
        """
        Delete a language.

        Args:
            language_id: ID of the language to delete

        Returns:
            Success message
        """
        return self.client.request("DELETE", f"/v1/languages/{language_id}")
