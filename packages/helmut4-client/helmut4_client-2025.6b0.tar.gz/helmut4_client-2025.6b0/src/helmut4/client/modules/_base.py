"""
Base module for Helmut4 client modules.
"""


class BaseModule:
    """Base class for API modules"""

    def __init__(self, client):
        self.client = client
