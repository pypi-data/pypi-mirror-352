"""
Comprehensive unit tests for TableConverter class.

This module contains exhaustive test cases covering all methods of the TableConverter class,
including both normal and error scenarios. Tests follow the AAA pattern with single assertions
and proper isolation using mocks.
"""

from typing import Any
from unittest.mock import patch

import pytest

from sphinxcontrib.jsontable.directives import (
    INVALID_JSON_DATA_ERROR,
    JsonTableError,
    TableConverter,
)

# Type aliases
JsonData = dict[str, Any] | list[Any]
TableData = list[list[str]]


# Test Fixtures
@pytest.fixture
def converter():
    """Create TableConverter instance for testing."""
    return TableConverter()


@pytest.fixture
def sample_dict():
    """Sample dictionary data for testing."""
    return {"name": "John", "age": 30, "city": "Tokyo"}


@pytest.fixture
def sample_list_of_dicts():
    """Sample list of dictionaries for testing."""
    return [{"name": "John", "age": 30}, {"name": "Jane", "age": 25, "city": "Osaka"}]


@pytest.fixture
def sample_list_of_lists():
    """Sample list of lists for testing."""
    return [["John", "30"], ["Jane", "25"]]


@pytest.fixture
def sample_headers():
    """Sample headers for testing."""
    return ["age", "name"]


class TestTableConverterConvert:
    """Test cases for the convert method."""

    def test_convert_dict_input_calls_convert_dict(self, converter):
        """Test convert method routes dict input to _convert_dict method."""
        # Arrange
        test_data = {"key": "value"}
        with patch.object(
            converter, "_convert_dict", return_value=[]
        ) as mock_convert_dict:
            # Act
            converter.convert(test_data, include_header=True, limit=10)
            # Assert
            mock_convert_dict.assert_called_once_with(test_data, True, 10)

    def test_convert_list_input_calls_convert_list(self, converter):
        """Test convert method routes list input to _convert_list method."""
        # Arrange
        test_data = [{"key": "value"}]
        with patch.object(
            converter, "_convert_list", return_value=[]
        ) as mock_convert_list:
            # Act
            converter.convert(test_data, include_header=False, limit=5)
            # Assert
            mock_convert_list.assert_called_once_with(test_data, False, 5)

    def test_convert_empty_data_raises_json_table_error(self, converter):
        """Test convert method raises JsonTableError for empty data."""
        # Act & Assert
        with pytest.raises(JsonTableError, match="No JSON data to process"):
            converter.convert(None, include_header=False)

    def test_convert_invalid_data_type_raises_json_table_error(self, converter):
        """Test convert method raises JsonTableError for invalid data types."""
        # Arrange
        invalid_data = "string_data"
        # Act & Assert
        with pytest.raises(JsonTableError, match=INVALID_JSON_DATA_ERROR):
            converter.convert(invalid_data)

    def test_convert_integer_data_raises_json_table_error(self, converter):
        """Test convert method raises JsonTableError for integer input."""
        # Arrange
        invalid_data = 123
        # Act & Assert
        with pytest.raises(JsonTableError, match=INVALID_JSON_DATA_ERROR):
            converter.convert(invalid_data)


class TestTableConverterConvertDict:
    """Test cases for the _convert_dict method."""

    def test_convert_dict_valid_data_calls_convert_object_list(
        self, converter, sample_dict
    ):
        """Test _convert_dict calls _convert_object_list with wrapped dict."""
        # Arrange
        with patch.object(
            converter, "_convert_object_list", return_value=[]
        ) as mock_convert:
            # Act
            converter._convert_dict(sample_dict, True, 5)
            # Assert
            mock_convert.assert_called_once_with([sample_dict], True, 5)

    def test_convert_dict_zero_limit_returns_empty_list(self, converter, sample_dict):
        """Test _convert_dict returns empty list when limit is zero."""
        # Arrange & Act
        result = converter._convert_dict(sample_dict, True, 0)
        # Assert
        assert result == []

    def test_convert_dict_negative_limit_returns_empty_list(
        self, converter, sample_dict
    ):
        """Test _convert_dict returns empty list when limit is negative."""
        # Arrange & Act
        result = converter._convert_dict(sample_dict, False, -1)
        # Assert
        assert result == []

    def test_convert_dict_none_limit_processes_data(self, converter, sample_dict):
        """Test _convert_dict processes data when limit is None."""
        # Arrange
        with patch.object(
            converter, "_convert_object_list", return_value=[["row1"]]
        ) as mock_convert:  # noqa
            # Act
            result = converter._convert_dict(sample_dict, False, None)
            # Assert
            assert result == [["row1"]]


class TestTableConverterConvertList:
    """Test cases for the _convert_list method."""

    def test_convert_list_empty_list_returns_empty_list(self, converter):
        """Test _convert_list returns empty list for empty input."""
        # Arrange & Act
        result = converter._convert_list([], True, None)
        # Assert
        assert result == []

    def test_convert_list_dict_items_calls_convert_object_list(
        self, converter, sample_list_of_dicts
    ):
        """Test _convert_list calls _convert_object_list for dict items."""
        # Arrange
        with patch.object(
            converter, "_convert_object_list", return_value=[]
        ) as mock_convert:
            # Act
            converter._convert_list(sample_list_of_dicts, True, 5)
            # Assert
            mock_convert.assert_called_once_with(sample_list_of_dicts, True, 5)

    def test_convert_list_array_items_calls_convert_array_list(
        self, converter, sample_list_of_lists
    ):
        """Test _convert_list calls _convert_array_list for array items."""
        # Arrange
        with patch.object(
            converter, "_convert_array_list", return_value=[]
        ) as mock_convert:
            # Act
            converter._convert_list(sample_list_of_lists, False, 3)
            # Assert
            mock_convert.assert_called_once_with(sample_list_of_lists, 3)

    def test_convert_list_none_first_element_raises_error(self, converter):
        """Test _convert_list raises error when first element is None."""
        # Arrange
        data_with_none = [None, {"key": "value"}]
        # Act & Assert
        with pytest.raises(
            JsonTableError, match="Invalid array data: null first element"
        ):
            converter._convert_list(data_with_none, False, None)

    def test_convert_list_invalid_first_element_raises_error(self, converter):
        """Test _convert_list raises error for invalid first element type."""
        # Arrange
        invalid_data = ["string", "another_string"]
        # Act & Assert
        with pytest.raises(
            JsonTableError, match="Array items must be objects or arrays"
        ):
            converter._convert_list(invalid_data, False, None)

    def test_convert_list_with_limit_processes_limited_data(
        self, converter, sample_list_of_dicts
    ):
        """Test _convert_list processes only limited data when limit is set."""
        # Arrange
        with patch.object(converter, "_convert_object_list") as mock_convert:
            # Act
            converter._convert_list(sample_list_of_dicts, True, 1)
            # Assert
            mock_convert.assert_called_once_with(sample_list_of_dicts[:1], True, 1)


class TestTableConverterConvertObjectList:
    """Test cases for the _convert_object_list method."""

    def test_convert_object_list_empty_list_returns_empty_list(self, converter):
        """Test _convert_object_list returns empty list for empty input."""
        # Arrange & Act
        result = converter._convert_object_list([], True, None)
        # Assert
        assert result == []

    def test_convert_object_list_with_header_includes_header_row(
        self, converter, sample_list_of_dicts
    ):
        """Test _convert_object_list includes header when include_header is True."""
        # Arrange
        with patch.object(converter, "_extract_headers", return_value=["age", "name"]):
            with patch.object(converter, "_object_to_row", return_value=["30", "John"]):
                # Act
                result = converter._convert_object_list(
                    sample_list_of_dicts, True, None
                )
                # Assert
                assert result[0] == ["age", "name"]

    def test_convert_object_list_without_header_excludes_header_row(
        self, converter, sample_list_of_dicts
    ):
        """Test _convert_object_list excludes header when include_header is False."""
        # Arrange
        with patch.object(converter, "_extract_headers", return_value=["age", "name"]):
            with patch.object(converter, "_object_to_row", return_value=["30", "John"]):
                # Act
                result = converter._convert_object_list(
                    sample_list_of_dicts, False, None
                )
                # Assert
                assert ["age", "name"] not in result

    def test_convert_object_list_calls_extract_headers(
        self, converter, sample_list_of_dicts
    ):
        """Test _convert_object_list calls _extract_headers method."""
        # Arrange
        with patch.object(
            converter, "_extract_headers", return_value=[]
        ) as mock_extract:
            with patch.object(converter, "_object_to_row", return_value=[]):
                # Act
                converter._convert_object_list(sample_list_of_dicts, False, None)
                # Assert
                mock_extract.assert_called_once_with(sample_list_of_dicts)

    def test_convert_object_list_applies_limit(self, converter, sample_list_of_dicts):
        """Test _convert_object_list applies limit to objects."""
        # Arrange
        with patch.object(converter, "_extract_headers", return_value=["name"]):
            with patch.object(
                converter, "_object_to_row", return_value=["John"]
            ) as mock_to_row:
                # Act
                converter._convert_object_list(sample_list_of_dicts, False, 1)
                # Assert
                assert mock_to_row.call_count == 1


class TestTableConverterConvertArrayList:
    """Test cases for the _convert_array_list method."""

    def test_convert_array_list_converts_all_elements_to_strings(
        self, converter, sample_list_of_lists
    ):
        """Test _convert_array_list converts all elements to strings."""
        # Arrange
        data_with_mixed_types = [[1, "John"], [2.5, "Jane"]]
        # Act
        result = converter._convert_array_list(data_with_mixed_types, None)
        # Assert
        assert result == [["1", "John"], ["2.5", "Jane"]]

    def test_convert_array_list_applies_limit(self, converter, sample_list_of_lists):
        """Test _convert_array_list applies limit to arrays."""
        # Arrange & Act
        result = converter._convert_array_list(sample_list_of_lists, 1)
        # Assert
        assert len(result) == 1

    def test_convert_array_list_handles_none_values(self, converter):
        """Test _convert_array_list handles None values correctly."""
        # Arrange
        data_with_none = [[None, "John"], ["Jane", None]]
        # Act
        result = converter._convert_array_list(data_with_none, None)
        # Assert
        assert result == [["", "John"], ["Jane", ""]]

    def test_convert_array_list_no_limit_processes_all_data(
        self, converter, sample_list_of_lists
    ):
        """Test _convert_array_list processes all data when no limit is set."""
        # Arrange & Act
        result = converter._convert_array_list(sample_list_of_lists, None)
        # Assert
        assert len(result) == len(sample_list_of_lists)


class TestTableConverterExtractHeaders:
    """Test cases for the _extract_headers method."""

    def test_extract_headers_single_object_returns_sorted_keys(self, converter):
        """Test _extract_headers returns sorted keys from single object."""
        # Arrange
        objects = [{"name": "John", "age": 30}]
        # Act
        result = converter._extract_headers(objects)
        # Assert
        assert result == ["age", "name"]

    def test_extract_headers_multiple_objects_merges_keys(
        self, converter, sample_list_of_dicts
    ):
        """Test _extract_headers merges keys from multiple objects."""
        # Arrange & Act
        result = converter._extract_headers(sample_list_of_dicts)
        # Assert
        assert set(result) == {"age", "city", "name"}

    def test_extract_headers_empty_list_returns_empty_list(self, converter):
        """Test _extract_headers returns empty list for empty input."""
        # Arrange & Act
        result = converter._extract_headers([])
        # Assert
        assert result == []

    def test_extract_headers_duplicate_keys_returns_unique_sorted_keys(self, converter):
        """Test _extract_headers returns unique sorted keys even with duplicates."""
        # Arrange
        objects = [{"name": "John"}, {"name": "Jane"}, {"age": 30}]
        # Act
        result = converter._extract_headers(objects)
        # Assert
        assert result == ["age", "name"]

    def test_extract_headers_maintains_alphabetical_order(self, converter):
        """Test _extract_headers maintains alphabetical order of keys."""
        # Arrange
        objects = [{"zebra": 1, "apple": 2, "banana": 3}]
        # Act
        result = converter._extract_headers(objects)
        # Assert
        assert result == ["apple", "banana", "zebra"]


class TestTableConverterObjectToRow:
    """Test cases for the _object_to_row method."""

    def test_object_to_row_all_keys_present_returns_values_in_order(
        self, converter, sample_headers
    ):
        """Test _object_to_row returns values in header order when all keys present."""
        # Arrange
        obj = {"name": "John", "age": "30"}
        # Act
        result = converter._object_to_row(obj, sample_headers)
        # Assert
        assert result == ["30", "John"]

    def test_object_to_row_missing_keys_returns_empty_strings(
        self, converter, sample_headers
    ):
        """Test _object_to_row returns empty strings for missing keys."""
        # Arrange
        obj = {"name": "John"}  # missing "age"
        # Act
        result = converter._object_to_row(obj, sample_headers)
        # Assert
        assert result == ["", "John"]

    def test_object_to_row_none_values_converted_to_empty_strings(
        self, converter, sample_headers
    ):
        """Test _object_to_row converts None values to empty strings."""
        # Arrange
        obj = {"name": None, "age": 30}
        # Act
        result = converter._object_to_row(obj, sample_headers)
        # Assert
        assert result == ["30", ""]

    def test_object_to_row_empty_object_returns_empty_strings(
        self, converter, sample_headers
    ):
        """Test _object_to_row returns empty strings for empty object."""
        # Arrange
        obj = {}
        # Act
        result = converter._object_to_row(obj, sample_headers)
        # Assert
        assert result == ["", ""]

    def test_object_to_row_converts_values_to_strings(self, converter):
        """Test _object_to_row converts all values to strings."""
        # Arrange
        obj = {"number": 123, "boolean": True, "float": 45.67}
        headers = ["boolean", "float", "number"]
        # Act
        result = converter._object_to_row(obj, headers)
        # Assert
        assert result == ["True", "45.67", "123"]

    def test_object_to_row_empty_headers_returns_empty_list(self, converter):
        """Test _object_to_row returns empty list for empty headers."""
        # Arrange
        obj = {"name": "John", "age": 30}
        headers = []
        # Act
        result = converter._object_to_row(obj, headers)
        # Assert
        assert result == []
