"""
Comprehensive unit tests for utility functions and JsonTableError class.

This test suite provides complete coverage for all utility functions,
following AAA (Arrange-Act-Assert) pattern with one assertion per test.
Tests cover normal operation, edge cases, and error scenarios.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import the functions and classes to be tested
from sphinxcontrib.jsontable import setup
from sphinxcontrib.jsontable.directives import (
    JsonTableError,
    ensure_file_exists,
    format_error,
    is_safe_path,
    safe_str,
    validate_not_empty,
)


class TestJsonTableError:
    """
    Test suite for JsonTableError exception class.

    Validates that JsonTableError behaves correctly as a custom exception
    with proper inheritance and message handling.
    """

    def test_json_table_error_inherits_from_exception(self):
        """Test that JsonTableError properly inherits from Exception."""
        # Arrange & Act
        error = JsonTableError("test message")

        # Assert
        assert isinstance(error, Exception)

    def test_json_table_error_can_be_instantiated_with_message(self):
        """Test that JsonTableError can be instantiated with a message."""
        # Arrange
        message = "Test error message"

        # Act
        error = JsonTableError(message)

        # Assert
        assert str(error) == message

    def test_json_table_error_can_be_raised_and_caught(self):
        """Test that JsonTableError can be raised and caught properly."""
        # Arrange
        message = "Test error"

        # Act & Assert
        with pytest.raises(JsonTableError) as exc_info:
            raise JsonTableError(message)

        assert str(exc_info.value) == message

    def test_json_table_error_can_be_instantiated_without_message(self):
        """Test that JsonTableError can be instantiated without arguments."""
        # Arrange & Act
        error = JsonTableError()

        # Assert
        assert str(error) == ""

    def test_json_table_error_preserves_multiple_arguments(self):
        """Test that JsonTableError preserves multiple arguments."""
        # Arrange
        arg1, arg2 = "first", "second"

        # Act
        error = JsonTableError(arg1, arg2)

        # Assert
        assert error.args == (arg1, arg2)


class TestValidateNotEmpty:
    """
    Test suite for validate_not_empty function.

    Validates that the function properly checks for empty/None data
    and raises JsonTableError with appropriate messages.
    """

    def test_validate_not_empty_with_none_raises_json_table_error(self):
        """Test that validate_not_empty raises JsonTableError when data is None."""
        # Arrange
        data = None
        error_msg = "Data cannot be None"

        # Act & Assert
        with pytest.raises(JsonTableError) as exc_info:
            validate_not_empty(data, error_msg)

        assert str(exc_info.value) == error_msg

    def test_validate_not_empty_with_empty_list_raises_json_table_error(self):
        """Test that validate_not_empty raises JsonTableError when data is empty list."""
        # Arrange
        data = []
        error_msg = "List cannot be empty"

        # Act & Assert
        with pytest.raises(JsonTableError) as exc_info:
            validate_not_empty(data, error_msg)

        assert str(exc_info.value) == error_msg

    def test_validate_not_empty_with_empty_string_raises_json_table_error(self):
        """Test that validate_not_empty raises JsonTableError when data is empty string."""
        # Arrange
        data = ""
        error_msg = "String cannot be empty"

        # Act & Assert
        with pytest.raises(JsonTableError) as exc_info:
            validate_not_empty(data, error_msg)

        assert str(exc_info.value) == error_msg

    def test_validate_not_empty_with_empty_dict_raises_json_table_error(self):
        """Test that validate_not_empty raises JsonTableError when data is empty dict."""
        # Arrange
        data = {}
        error_msg = "Dict cannot be empty"

        # Act & Assert
        with pytest.raises(JsonTableError) as exc_info:
            validate_not_empty(data, error_msg)

        assert str(exc_info.value) == error_msg

    def test_validate_not_empty_with_zero_raises_json_table_error(self):
        """Test that validate_not_empty raises JsonTableError when data is zero."""
        # Arrange
        data = 0
        error_msg = "Value cannot be zero"

        # Act & Assert
        with pytest.raises(JsonTableError) as exc_info:
            validate_not_empty(data, error_msg)

        assert str(exc_info.value) == error_msg

    def test_validate_not_empty_with_false_raises_json_table_error(self):
        """Test that validate_not_empty raises JsonTableError when data is False."""
        # Arrange
        data = False
        error_msg = "Value cannot be False"

        # Act & Assert
        with pytest.raises(JsonTableError) as exc_info:
            validate_not_empty(data, error_msg)

        assert str(exc_info.value) == error_msg

    def test_validate_not_empty_with_non_empty_list_does_not_raise(self):
        """Test that validate_not_empty does not raise when data is non-empty list."""
        # Arrange
        data = [1, 2, 3]
        error_msg = "Should not be raised"

        # Act (should not raise)
        try:
            validate_not_empty(data, error_msg)
            success = True
        except JsonTableError:
            success = False

        # Assert
        assert success is True

    def test_validate_not_empty_with_non_empty_string_does_not_raise(self):
        """Test that validate_not_empty does not raise when data is non-empty string."""
        # Arrange
        data = "non-empty"
        error_msg = "Should not be raised"

        # Act (should not raise)
        try:
            validate_not_empty(data, error_msg)
            success = True
        except JsonTableError:
            success = False

        # Assert
        assert success is True

    def test_validate_not_empty_with_non_empty_dict_does_not_raise(self):
        """Test that validate_not_empty does not raise when data is non-empty dict."""
        # Arrange
        data = {"key": "value"}
        error_msg = "Should not be raised"

        # Act (should not raise)
        try:
            validate_not_empty(data, error_msg)
            success = True
        except JsonTableError:
            success = False

        # Assert
        assert success is True

    def test_validate_not_empty_with_positive_number_does_not_raise(self):
        """Test that validate_not_empty does not raise when data is positive number."""
        # Arrange
        data = 42
        error_msg = "Should not be raised"

        # Act (should not raise)
        try:
            validate_not_empty(data, error_msg)
            success = True
        except JsonTableError:
            success = False

        # Assert
        assert success is True


class TestSafeStr:
    """
    Test suite for safe_str function.

    Validates that the function safely converts various types to strings
    and handles None values appropriately.
    """

    def test_safe_str_with_none_returns_empty_string(self):
        """Test that safe_str returns empty string when value is None."""
        # Arrange
        value = None

        # Act
        result = safe_str(value)

        # Assert
        assert result == ""

    def test_safe_str_with_string_returns_same_string(self):
        """Test that safe_str returns the same string when value is string."""
        # Arrange
        value = "test string"

        # Act
        result = safe_str(value)

        # Assert
        assert result == "test string"

    def test_safe_str_with_integer_returns_string_representation(self):
        """Test that safe_str returns string representation when value is integer."""
        # Arrange
        value = 42

        # Act
        result = safe_str(value)

        # Assert
        assert result == "42"

    def test_safe_str_with_float_returns_string_representation(self):
        """Test that safe_str returns string representation when value is float."""
        # Arrange
        value = 3.14

        # Act
        result = safe_str(value)

        # Assert
        assert result == "3.14"

    def test_safe_str_with_boolean_true_returns_true_string(self):
        """Test that safe_str returns 'True' when value is boolean True."""
        # Arrange
        value = True

        # Act
        result = safe_str(value)

        # Assert
        assert result == "True"

    def test_safe_str_with_boolean_false_returns_false_string(self):
        """Test that safe_str returns 'False' when value is boolean False."""
        # Arrange
        value = False

        # Act
        result = safe_str(value)

        # Assert
        assert result == "False"

    def test_safe_str_with_list_returns_string_representation(self):
        """Test that safe_str returns string representation when value is list."""
        # Arrange
        value = [1, 2, 3]

        # Act
        result = safe_str(value)

        # Assert
        assert result == "[1, 2, 3]"

    def test_safe_str_with_dict_returns_string_representation(self):
        """Test that safe_str returns string representation when value is dict."""
        # Arrange
        value = {"key": "value"}

        # Act
        result = safe_str(value)

        # Assert
        assert result == "{'key': 'value'}"

    def test_safe_str_with_custom_object_calls_str_method(self):
        """Test that safe_str calls __str__ method on custom objects."""

        # Arrange
        class CustomObject:
            def __str__(self):
                return "custom string representation"

        value = CustomObject()

        # Act
        result = safe_str(value)

        # Assert
        assert result == "custom string representation"

    def test_safe_str_with_zero_returns_zero_string(self):
        """Test that safe_str returns '0' when value is zero."""
        # Arrange
        value = 0

        # Act
        result = safe_str(value)

        # Assert
        assert result == "0"


class TestEnsureFileExists:
    """
    Test suite for ensure_file_exists function.

    Validates that the function properly checks file existence
    and raises FileNotFoundError when appropriate.
    """

    @patch("pathlib.Path.exists")
    def test_ensure_file_exists_with_existing_file_does_not_raise(self, mock_exists):
        """Test that ensure_file_exists does not raise when file exists."""
        # Arrange
        mock_exists.return_value = True
        file_path = Path("/fake/path/file.txt")

        # Act (should not raise)
        try:
            ensure_file_exists(file_path)
            success = True
        except FileNotFoundError:
            success = False

        # Assert
        assert success is True

    @patch("pathlib.Path.exists")
    def test_ensure_file_exists_with_non_existing_file_raises_file_not_found_error(
        self, mock_exists
    ):
        """Test that ensure_file_exists raises FileNotFoundError when file does not exist."""
        # Arrange
        mock_exists.return_value = False
        file_path = Path("/fake/path/missing.txt")

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            ensure_file_exists(file_path)

    @patch("pathlib.Path.exists")
    def test_ensure_file_exists_error_message_contains_file_path(self, mock_exists):
        """Test that ensure_file_exists error message contains the file path."""
        # Arrange
        mock_exists.return_value = False
        file_path = Path("/fake/path/missing.txt")

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            ensure_file_exists(file_path)

        assert str(file_path) in str(exc_info.value)

    @patch("pathlib.Path.exists")
    def test_ensure_file_exists_error_message_format(self, mock_exists):
        """Test that ensure_file_exists error message has correct format."""
        # Arrange
        mock_exists.return_value = False
        file_path = Path("/fake/path/missing.txt")
        expected_message = f"JSON file not found: {file_path}"

        # Act & Assert
        with pytest.raises(FileNotFoundError) as exc_info:
            ensure_file_exists(file_path)

        assert str(exc_info.value) == expected_message

    @patch("pathlib.Path.exists")
    def test_ensure_file_exists_calls_path_exists_method(self, mock_exists):
        """Test that ensure_file_exists calls the exists method on the path."""
        # Arrange
        mock_exists.return_value = True
        file_path = Path("/fake/path/file.txt")

        # Act
        ensure_file_exists(file_path)

        # Assert
        mock_exists.assert_called_once()


class TestFormatError:
    """
    Test suite for format_error function.

    Validates that the function properly formats error messages
    combining context and exception details.
    """

    def test_format_error_combines_context_and_exception_message(self):
        """Test that format_error combines context and exception message correctly."""
        # Arrange
        context = "Test operation"
        error = ValueError("Test error message")
        expected = "Test operation: Test error message"

        # Act
        result = format_error(context, error)

        # Assert
        assert result == expected

    def test_format_error_with_different_exception_types(self):
        """Test that format_error works with different exception types."""
        # Arrange
        context = "JSON parsing"
        error = JsonTableError("Invalid JSON format")
        expected = "JSON parsing: Invalid JSON format"

        # Act
        result = format_error(context, error)

        # Assert
        assert result == expected

    def test_format_error_with_empty_context_string(self):
        """Test that format_error handles empty context string."""
        # Arrange
        context = ""
        error = RuntimeError("Runtime issue")
        expected = ": Runtime issue"

        # Act
        result = format_error(context, error)

        # Assert
        assert result == expected

    def test_format_error_with_exception_without_message(self):
        """Test that format_error handles exception without message."""
        # Arrange
        context = "Operation failed"
        error = ValueError()
        expected = "Operation failed: "

        # Act
        result = format_error(context, error)

        # Assert
        assert result == expected

    def test_format_error_with_file_not_found_error(self):
        """Test that format_error works with FileNotFoundError."""
        # Arrange
        context = "File loading"
        error = FileNotFoundError("File not found")
        expected = "File loading: File not found"

        # Act
        result = format_error(context, error)

        # Assert
        assert result == expected

    def test_format_error_returns_string_type(self):
        """Test that format_error returns a string type."""
        # Arrange
        context = "Test"
        error = Exception("Test")

        # Act
        result = format_error(context, error)

        # Assert
        assert isinstance(result, str)


class TestIsSafePath:
    """
    Test suite for is_safe_path function.

    Validates that the function properly prevents directory traversal attacks
    and handles different path scenarios correctly.
    """

    @patch("pathlib.Path.resolve")
    def test_is_safe_path_with_safe_subdirectory_returns_true(self, mock_resolve):
        """Test that is_safe_path returns True for safe subdirectory paths."""
        # Arrange
        base_path = Path("/base/dir")
        safe_path = Path("/base/dir/subdir/file.txt")

        mock_resolve.side_effect = (
            lambda: safe_path if mock_resolve.call_count == 1 else base_path
        )

        # Mock is_relative_to method
        with patch.object(Path, "is_relative_to", return_value=True):
            # Act
            result = is_safe_path(safe_path, base_path)

        # Assert
        assert result is True

    @patch("pathlib.Path.resolve")
    def test_is_safe_path_with_directory_traversal_returns_false(self, mock_resolve):
        """Test that is_safe_path returns False for directory traversal attempts."""
        # Arrange
        base_path = Path("/base/dir")
        unsafe_path = Path("/base/dir/../../../etc/passwd")

        mock_resolve.side_effect = (
            lambda: unsafe_path if mock_resolve.call_count == 1 else base_path
        )

        # Mock is_relative_to method
        with patch.object(Path, "is_relative_to", return_value=False):
            # Act
            result = is_safe_path(unsafe_path, base_path)

        # Assert
        assert result is False

    @patch("pathlib.Path.resolve")
    def test_is_safe_path_with_absolute_path_outside_base_returns_false(
        self, mock_resolve
    ):
        """Test that is_safe_path returns False for absolute paths outside base."""
        # Arrange
        base_path = Path("/base/dir")
        outside_path = Path("/other/dir/file.txt")

        mock_resolve.side_effect = (
            lambda: outside_path if mock_resolve.call_count == 1 else base_path
        )

        # Mock is_relative_to method
        with patch.object(Path, "is_relative_to", return_value=False):
            # Act
            result = is_safe_path(outside_path, base_path)

        # Assert
        assert result is False

    @patch("pathlib.Path.resolve")
    def test_is_safe_path_with_same_directory_returns_true(self, mock_resolve):
        """Test that is_safe_path returns True for same directory path."""
        # Arrange
        base_path = Path("/base/dir")
        same_path = Path("/base/dir")

        mock_resolve.side_effect = (
            lambda: same_path if mock_resolve.call_count == 1 else base_path
        )

        # Mock is_relative_to method
        with patch.object(Path, "is_relative_to", return_value=True):
            # Act
            result = is_safe_path(same_path, base_path)

        # Assert
        assert result is True

    @patch("pathlib.Path.resolve")
    def test_is_safe_path_handles_attribute_error_falls_back_to_relative_to(
        self, mock_resolve
    ):
        """Test that is_safe_path handles AttributeError and falls back to relative_to method."""
        # Arrange
        base_path = Path("/base/dir")
        test_path = Path("/base/dir/file.txt")

        resolved_test_path = Mock()
        resolved_base_path = Mock()

        # Set up resolve to return the appropriate mock for each call
        def resolve_side_effect():
            if mock_resolve.call_count <= 2:
                return resolved_test_path
            else:
                return resolved_base_path

        mock_resolve.side_effect = [
            resolved_test_path,
            resolved_base_path,
            resolved_test_path,
            resolved_base_path,
        ]

        # Mock is_relative_to to raise AttributeError (older Python versions)
        resolved_test_path.is_relative_to.side_effect = AttributeError(
            "No is_relative_to method"
        )

        # Mock relative_to to succeed (fallback) - it should not raise any exception
        resolved_test_path.relative_to.return_value = Path("file.txt")

        # Act
        result = is_safe_path(test_path, base_path)

        # Assert
        assert result is True

    @patch("pathlib.Path.resolve")
    def test_is_safe_path_handles_exception_in_fallback_returns_false(
        self, mock_resolve
    ):
        """Test that is_safe_path returns False when exception occurs in fallback."""
        # Arrange
        base_path = Path("/base/dir")
        test_path = Path("/outside/dir/file.txt")

        resolved_test_path = Mock()
        resolved_base_path = Mock()

        mock_resolve.side_effect = [resolved_test_path, resolved_base_path]

        # Mock is_relative_to to raise AttributeError
        resolved_test_path.is_relative_to.side_effect = AttributeError(
            "No is_relative_to method"
        )

        # Mock relative_to to raise exception (path not relative)
        resolved_test_path.relative_to.side_effect = ValueError("Path not relative")

        # Act
        result = is_safe_path(test_path, base_path)

        # Assert
        assert result is False

    @patch("pathlib.Path.resolve")
    def test_is_safe_path_calls_resolve_on_both_paths(self, mock_resolve):
        """Test that is_safe_path calls resolve on both input paths."""
        # Arrange
        base_path = Path("/base/dir")
        test_path = Path("/base/dir/file.txt")

        resolved_mock = Mock()
        resolved_mock.is_relative_to.return_value = True
        mock_resolve.return_value = resolved_mock

        # Act
        is_safe_path(test_path, base_path)

        # Assert
        assert mock_resolve.call_count == 2

    def test_is_safe_path_returns_boolean_type(self):
        """Test that is_safe_path always returns a boolean value."""
        # Arrange
        base_path = Path("/base/dir")
        test_path = Path("/base/dir/file.txt")

        # Act
        result = is_safe_path(test_path, base_path)

        # Assert
        assert isinstance(result, bool)


class DummyApp:
    def add_directive(self, name, directive):
        self.called = (name, directive)


def test_setup_returns_metadata():
    app = DummyApp()
    meta = setup(app)
    assert isinstance(meta, dict)
    assert "version" in meta
    assert meta["parallel_read_safe"] is True
    assert meta["parallel_write_safe"] is True
