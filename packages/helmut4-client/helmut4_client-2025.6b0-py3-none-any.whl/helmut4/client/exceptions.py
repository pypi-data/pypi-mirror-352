"""
Exceptions for the Helmut4 client library.
"""


class Helmut4Error(Exception):
    """Base exception for Helmut4 API errors"""

    def __init__(
        self, message: str, status_code: int = None, response: dict = None
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)
