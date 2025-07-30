"""
Main client implementation for Helmut4 API.
"""

import logging
from typing import Any
from urllib.parse import urljoin

import requests

from .exceptions import Helmut4Error
from .modules import (
    AssetsModule,
    CronjobModule,
    GroupsModule,
    JobsModule,
    LanguagesModule,
    LicenseModule,
    MetadataModule,
    PreferencesModule,
    ProjectsModule,
    StreamsModule,
    UsersModule,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Helmut4Client:
    """
    Main client for interacting with Helmut4 API.
    """

    def __init__(
        self,
        base_url: str,
        username: str = None,
        password: str = None,
        token: str = None,
    ):
        """
        Initialize the Helmut4 client.

        Args:
            base_url: Base URL of the Helmut4 instance (e.g. http://localhost
                or https://helmut.example.com)
            username: Username for authentication
            password: Password for authentication
            token: JWT token for authentication (alternative to
                username/password)
        """
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.token = token
        self.session = requests.Session()

        # Initialize API modules
        self.users = UsersModule(self)
        self.groups = GroupsModule(self)
        self.projects = ProjectsModule(self)
        self.assets = AssetsModule(self)
        self.jobs = JobsModule(self)
        self.streams = StreamsModule(self)
        self.metadata = MetadataModule(self)
        self.preferences = PreferencesModule(self)
        self.cronjobs = CronjobModule(self)
        self.languages = LanguagesModule(self)
        self.licenses = LicenseModule(self)

        # Authenticate if credentials are provided
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        elif username and password:
            self.authenticate()

    def authenticate(self) -> str:
        """
        Authenticate with the Helmut4 API and obtain a JWT token.

        Returns:
            The JWT token string.

        Raises:
            Helmut4Error: If authentication fails.
        """
        auth_url = urljoin(self.base_url, "/v1/members/auth/login/body")

        try:
            response = self.session.post(
                auth_url,
                json={
                    "username": self.username,
                    "password": self.password
                },
            )

            response.raise_for_status()

            # Extract token from header or response body
            token = None
            auth_header = response.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

            # If token is not in header, check response body
            if not token and response.json():
                token = response.json().get("token")

            if not token:
                raise Helmut4Error(
                    "Authentication successful but no token received"
                )

            self.token = token
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            return token

        except requests.exceptions.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                status_code = e.response.status_code
                try:
                    error_data = e.response.json()
                except requests.exceptions.JSONDecodeError:
                    error_data = {"error": e.response.text}

                raise Helmut4Error(
                    f"Authentication failed: {e}",
                    status_code=status_code,
                    response=error_data,
                ) from e
            raise Helmut4Error(f"Authentication failed: {e}") from e

    def request(self, method: str, path: str, **kwargs) -> Any:
        """
        Make a request to the Helmut4 API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API path (will be joined with base_url)
            **kwargs: Additional arguments to pass to requests

        Returns:
            The JSON response (parsed into Python objects)

        Raises:
            Helmut4Error: If the request fails
        """
        url = urljoin(self.base_url, path)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            # Return raw content for binary responses
            if "octet-stream" in response.headers.get("Content-Type", ""):
                return response.content

            # Try parsing as JSON, fallback to text
            try:
                return response.json()
            except ValueError:
                return response.text

        except requests.exceptions.RequestException as e:
            if hasattr(e, "response") and e.response is not None:
                status_code = e.response.status_code
                try:
                    error_data = e.response.json()
                except requests.exceptions.JSONDecodeError:
                    error_data = {"error": e.response.text}

                raise Helmut4Error(
                    f"Request failed: {e}",
                    status_code=status_code,
                    response=error_data,
                ) from e
            raise Helmut4Error(f"Request failed: {e}") from e
