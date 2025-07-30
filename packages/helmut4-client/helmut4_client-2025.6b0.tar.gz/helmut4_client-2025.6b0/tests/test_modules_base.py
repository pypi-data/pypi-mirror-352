"""
Unit tests for base module functionality.
"""

from unittest.mock import Mock

from helmut4.client.modules._base import BaseModule


class TestBaseModule:
    """Test BaseModule class."""

    def test_init(self):
        """Test BaseModule initialization."""
        mock_client = Mock()
        module = BaseModule(mock_client)

        assert module.client is mock_client

    def test_client_assignment(self):
        """Test that client is properly assigned."""
        mock_client = Mock()
        mock_client.base_url = "https://test.example.com"
        mock_client.token = "test-token"

        module = BaseModule(mock_client)

        assert module.client.base_url == "https://test.example.com"
        assert module.client.token == "test-token"

    def test_inheritance(self):
        """Test that BaseModule can be inherited."""
        mock_client = Mock()

        class TestModule(BaseModule):

            def test_method(self):
                return self.client.request("GET", "/test")

        module = TestModule(mock_client)
        assert hasattr(module, "client")
        assert hasattr(module, "test_method")

        # Test that inherited method can access client
        mock_client.request.return_value = {"success": True}
        result = module.test_method()
        assert result == {"success": True}
        mock_client.request.assert_called_once_with("GET", "/test")
