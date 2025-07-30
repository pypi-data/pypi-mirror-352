"""
Unit tests for Helmut4 client exceptions.
"""

import pytest

from helmut4.client.exceptions import Helmut4Error


class TestHelmut4Error:
    """Test Helmut4Error exception class."""

    def test_init_message_only(self):
        """Test initialization with message only."""
        error = Helmut4Error("Test error message")

        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.status_code is None
        assert error.response is None

    def test_init_with_status_code(self):
        """Test initialization with status code."""
        error = Helmut4Error("Bad Request", status_code=400)

        assert str(error) == "Bad Request"
        assert error.message == "Bad Request"
        assert error.status_code == 400
        assert error.response is None

    def test_init_with_response(self):
        """Test initialization with response data."""
        response_data = {
            "error": "Validation failed",
            "details": ["Field required"],
        }
        error = Helmut4Error("Validation error", response=response_data)

        assert str(error) == "Validation error"
        assert error.message == "Validation error"
        assert error.status_code is None
        assert error.response == response_data

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters."""
        response_data = {"error": "Not Found", "resource": "user"}
        error = Helmut4Error(
            "User not found", status_code=404, response=response_data
        )

        assert str(error) == "User not found"
        assert error.message == "User not found"
        assert error.status_code == 404
        assert error.response == response_data

    def test_inheritance_from_exception(self):
        """Test that Helmut4Error inherits from Exception."""
        error = Helmut4Error("Test error")

        assert isinstance(error, Exception)
        assert isinstance(error, Helmut4Error)

    def test_can_be_raised_and_caught(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(Helmut4Error) as exc_info:
            raise Helmut4Error("Test exception", status_code=500)

        assert exc_info.value.message == "Test exception"
        assert exc_info.value.status_code == 500

    def test_can_be_caught_as_general_exception(self):
        """Test that Helmut4Error can be caught as general Exception."""
        with pytest.raises(Exception) as exc_info:
            raise Helmut4Error("Test exception")

        assert isinstance(exc_info.value, Helmut4Error)
        assert str(exc_info.value) == "Test exception"

    def test_error_attributes_immutable_after_creation(self):
        """Test that error attributes can be modified after creation."""
        error = Helmut4Error("Original message")

        # These should be modifiable (not enforced immutability)
        error.message = "Modified message"
        error.status_code = 400
        error.response = {"new": "data"}

        assert error.message == "Modified message"
        assert error.status_code == 400
        assert error.response == {"new": "data"}

    def test_repr_method(self):
        """Test string representation of error."""
        error = Helmut4Error("Test error", status_code=400)

        # The default repr should include the class name and message
        repr_str = repr(error)
        assert "Helmut4Error" in repr_str
        assert "Test error" in repr_str
