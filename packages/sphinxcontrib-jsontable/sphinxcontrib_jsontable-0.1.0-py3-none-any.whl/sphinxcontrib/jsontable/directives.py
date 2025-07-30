"""
json_table_directive.py

Sphinx directive for rendering JSON (file or inline) as ReStructuredText tables.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

logger = logging.getLogger(__name__)

JsonData = list[Any] | dict[str, Any]
TableData = list[list[str]]

DEFAULT_ENCODING = "utf-8"
NO_JSON_SOURCE_ERROR = "No JSON data source provided"
INVALID_JSON_DATA_ERROR = "JSON data must be an array or object"
EMPTY_CONTENT_ERROR = "No inline JSON content provided"


class JsonTableError(Exception):
    """
    Exception raised for errors that occur during JSON to table conversion.

    Attributes:
        message -- explanation of the error
    """


def validate_not_empty(data: Any, error_msg: str) -> None:
    """
    Raise JsonTableError with the given message if data is None or empty.

    Args:
        data: The data to validate, may be None or an empty sequence.
        error_msg: Error message for exception when data is empty.
    """
    if not data:
        raise JsonTableError(error_msg)


def safe_str(value: Any) -> str:
    """
    Safely convert a value to string, returning empty string for None.

    Args:
        value: Any value to convert to string.

    Returns:
        String representation of value, or empty string if value is None.
    """
    return str(value) if value is not None else ""


def ensure_file_exists(path: Path) -> None:
    """
    Check that the given file path exists; raise FileNotFoundError if not.

    Args:
        path: Path object representing the file path to check.

    Raises:
        FileNotFoundError: If the file does not exist at the given path.
    """
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")


def format_error(context: str, error: Exception) -> str:
    """
    Format an error message combining a context string with exception details.

    Args:
        context: Description of the operation or location where the error occurred.
        error: Exception instance containing details about the error.

    Returns:
        A formatted string "{context}: {error}".
    """
    return f"{context}: {error}"


def is_safe_path(path: Path, base: Path) -> bool:
    """
    Determine if a given path is a subpath of a base directory to prevent directory traversal.

    Args:
        path: The Path to validate.
        base: The base directory Path against which to validate.

    Returns:
        True if path is within base directory, False otherwise.
    """
    try:
        return path.resolve().is_relative_to(base.resolve())
    except AttributeError:
        try:
            path.resolve().relative_to(base.resolve())
            return True
        except Exception:
            return False


class JsonDataLoader:
    """
    Loader class for reading JSON data from files or inline content.

    Args:
        encoding: Character encoding to use when reading files (default: "utf-8").
    """

    def __init__(self, encoding: str = DEFAULT_ENCODING):
        self.encoding = self._validate_encoding(encoding)

    def _validate_encoding(self, encoding: str) -> str:
        """
        Validate provided encoding; return default if invalid.

        Args:
            encoding: Encoding name to validate.

        Returns:
            Validated encoding name, or DEFAULT_ENCODING if invalid.
        """
        try:
            "test".encode(encoding)
            return encoding
        except LookupError:
            logger.warning(f"Invalid encoding '{encoding}', using {DEFAULT_ENCODING}")
            return DEFAULT_ENCODING

    def _validate_file_path(self, source: str, srcdir: Path) -> Path:
        """
        Validate and resolve a JSON file path relative to a source directory.

        Args:
            source: Relative path string to the JSON file.
            srcdir: Base directory Path for resolving the source.

        Returns:
            Resolved Path object for the JSON file.

        Raises:
            JsonTableError: If the path is unsafe (directory traversal).
        """
        file_path = srcdir / source
        if not is_safe_path(file_path, srcdir):
            raise JsonTableError(f"Invalid file path: {source}")
        return file_path

    def load_from_file(self, source: str, srcdir: Path) -> JsonData:
        """
        Load JSON data from a file within the Sphinx source directory.

        Args:
            source: Relative file path to JSON.
            srcdir: Path of the Sphinx project source directory.

        Returns:
            Parsed JSON data (object or array).

        Raises:
            JsonTableError: If path validation fails or JSON decoding fails.
            FileNotFoundError: If the file does not exist.
        """
        file_path = self._validate_file_path(source, srcdir)
        ensure_file_exists(file_path)

        try:
            with open(file_path, encoding=self.encoding) as f:
                return json.load(f)
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise JsonTableError(format_error(f"Failed to load {source}", e)) from e

    def parse_inline(self, content: list[str]) -> JsonData:
        """
        Parse inline JSON content provided as lines of text.

        Args:
            content: List of strings representing lines of JSON.

        Returns:
            Parsed JSON data (object or array).

        Raises:
            JsonTableError: If content is empty or invalid JSON.
        """
        validate_not_empty(content, EMPTY_CONTENT_ERROR)

        try:
            return json.loads("\n".join(content))
        except json.JSONDecodeError as e:
            raise JsonTableError(f"Invalid inline JSON: {e.msg}") from e


class TableConverter:
    """
    Convert JSON data into a 2D list (TableData) suitable for table building.

    Methods:
        convert: Entry point for conversion of object or array.
    """

    def convert(
        self,
        data: JsonData,
        include_header: bool = False,
        limit: int | None = None,
    ) -> TableData:
        """
        Convert JSON data to a list of rows, optionally including headers and limiting rows.

        Args:
            data: JSON data as dict or list.
            include_header: Whether to include header row (default False).
            limit: Maximum number of rows to include (None for no limit).

        Returns:
            TableData: A list of rows, each row itself a list of strings.

        Raises:
            JsonTableError: If data is not dict or list, or if empty.
        """
        validate_not_empty(data, "No JSON data to process")

        if isinstance(data, dict):
            return self._convert_dict(data, include_header, limit)
        elif isinstance(data, list):
            return self._convert_list(data, include_header, limit)
        else:
            raise JsonTableError(INVALID_JSON_DATA_ERROR)

    def _convert_dict(
        self,
        data: dict[str, Any],
        include_header: bool,
        limit: int | None = None,
    ) -> TableData:
        """
        Convert a single JSON object into table rows, considering limit.

        Args:
            data: JSON object as dict.
            include_header: Whether to include a header row.
            limit: Row limit (None or positive integer).

        Returns:
            TableData rows for the object.
        """
        if limit is not None and limit <= 0:
            return []
        return self._convert_object_list([data], include_header, limit)

    def _convert_list(
        self,
        data: list[Any],
        include_header: bool,
        limit: int | None = None,
    ) -> TableData:
        """
        Convert a JSON array into table rows, dispatching by element type.

        Args:
            data: JSON array as list.
            include_header: Whether to include headers for objects.
            limit: Row limit.

        Returns:
            TableData rows for the array.

        Raises:
            JsonTableError: If first element is null or unsupported type.
        """
        if not data:
            return []
        limited_data = data[:limit] if limit is not None else data
        first_item = limited_data[0]
        if first_item is None:
            raise JsonTableError("Invalid array data: null first element")

        if isinstance(first_item, dict):
            return self._convert_object_list(limited_data, include_header, limit)
        elif isinstance(first_item, list):
            return self._convert_array_list(limited_data, limit)
        else:
            raise JsonTableError("Array items must be objects or arrays")

    def _convert_object_list(
        self,
        objects: list[dict[str, Any]],
        include_header: bool,
        limit: int | None = None,
    ) -> TableData:
        """
        Convert a list of JSON objects into rows, extracting headers.

        Args:
            objects: List of dicts.
            include_header: Whether to prepend header row.
            limit: Row limit.

        Returns:
            TableData with optional header and rows.
        """
        if not objects:
            return []
        headers = self._extract_headers(objects)
        limited_objects = objects[:limit] if limit is not None else objects
        rows = [self._object_to_row(obj, headers) for obj in limited_objects]
        return [headers, *rows] if include_header else rows

    def _convert_array_list(
        self,
        arrays: list[list[Any]],
        limit: int | None = None,
    ) -> TableData:
        """
        Convert a list of arrays (lists) directly into rows.

        Args:
            arrays: List of lists representing rows.
            limit: Row limit.

        Returns:
            TableData rows with all elements stringified.
        """
        limited_arrays = arrays[:limit] if limit is not None else arrays
        return [[safe_str(cell) for cell in row] for row in limited_arrays]

    def _extract_headers(self, objects: list[dict[str, Any]]) -> list[str]:
        """
        Extract sorted header names from a list of JSON objects.

        Args:
            objects: List of dicts from which to collect keys.

        Returns:
            Alphabetically sorted list of unique keys.
        """
        all_keys = set()
        for obj in objects:
            all_keys.update(obj.keys())
        return sorted(all_keys)

    def _object_to_row(self, obj: dict[str, Any], headers: list[str]) -> list[str]:
        """
        Convert a JSON object to a row based on provided headers.

        Args:
            obj: JSON object dict.
            headers: List of header names to use as columns.

        Returns:
            List of stringified values corresponding to headers.
        """
        return [safe_str(obj.get(key, "")) for key in headers]


class TableBuilder:
    """
    Build docutils.table nodes from TableData for Sphinx documentation.

    Methods:
        build: Create and populate table nodes with header/body.
    """

    def build(self, table_data: TableData, has_header: bool = False) -> nodes.table:
        """
        Build a docutils.nodes.table from 2D list of strings.

        Args:
            table_data: 2D list representing table content.
            has_header: Whether the first row is a header (default False).

        Returns:
            nodes.table node ready for inclusion in document.
        """
        if not table_data:
            return self._create_empty_table()

        max_cols = max(len(row) for row in table_data)
        table = self._create_table_structure(max_cols)

        if has_header:
            self._add_header(table, table_data[0])
            body_data = table_data[1:]
        else:
            body_data = table_data

        self._add_body(table, body_data, max_cols)
        return table

    def _create_empty_table(self) -> nodes.table:
        """
        Create an empty table node with one column.

        Returns:
            nodes.table with a single colspec.
        """
        table = nodes.table()
        tgroup = nodes.tgroup(cols=1)
        table += tgroup
        return table

    def _create_table_structure(self, cols: int) -> nodes.table:
        """
        Create a table structure with given number of columns.

        Args:
            cols: Number of columns for the table.

        Returns:
            nodes.table with tgroup and colspec elements.
        """
        table = nodes.table()
        tgroup = nodes.tgroup(cols=cols)
        table += tgroup

        for _ in range(cols):
            tgroup += nodes.colspec(colwidth=1)

        return table

    def _add_header(self, table: nodes.table, header_data: list[str]) -> None:
        """
        Add a header row to an existing table node.

        Args:
            table: nodes.table to modify.
            header_data: List of header cell strings.
        """
        thead = nodes.thead()
        header_row = self._create_row(header_data)
        thead += header_row
        table[0] += thead

    def _add_body(
        self,
        table: nodes.table,
        body_data: TableData,
        max_cols: int,
    ) -> None:
        """
        Add body rows to an existing table node.

        Args:
            table: nodes.table to modify.
            body_data: 2D list for body rows.
            max_cols: Maximum number of columns for padding.
        """
        tbody = nodes.tbody()

        for row_data in body_data:
            padded_row = row_data + [""] * (max_cols - len(row_data))
            tbody += self._create_row(padded_row)

        table[0] += tbody

    def _create_row(self, row_data: list[str]) -> nodes.row:
        """
        Create a docutils row node from a list of cell strings.

        Args:
            row_data: List of strings for each cell in the row.

        Returns:
            nodes.row containing entry and paragraph nodes.
        """
        row = nodes.row()
        for cell_data in row_data:
            entry = nodes.entry()
            entry += nodes.paragraph(text=cell_data)
            row += entry
        return row


class JsonTableDirective(SphinxDirective):
    """
    Sphinx directive to render JSON data as a reStructuredText table.

    Options:
        header: Flag to include the first row of JSON objects as table header.
        encoding: Character encoding for JSON file reading.
        limit: Positive integer to limit the number of rows.
    """

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    option_spec: ClassVar[dict] = {
        "header": directives.flag,
        "encoding": directives.unchanged,
        "limit": directives.positive_int,  # Accept only positive integers
    }

    def __init__(self, *args, **kwargs):
        """
        Initialize directive with JSON loader, converter, and builder.
        """
        super().__init__(*args, **kwargs)
        encoding = self.options.get("encoding", DEFAULT_ENCODING)
        self.loader = JsonDataLoader(encoding)
        self.converter = TableConverter()
        self.builder = TableBuilder()

    def run(self) -> list[nodes.Node]:
        """
        Execute the directive: load JSON, convert to table_data,
        build table node, and return it.

        Returns:
            List of docutils.nodes.Node (table or error node).
        """
        try:
            json_data = self._load_json_data()
            include_header = "header" in self.options
            limit = self.options.get("limit")  # None or positive integer

            # Output debug information to log
            if limit is not None:
                logger.info(f"JsonTable: Limiting output to {limit} rows")

            table_data = self.converter.convert(json_data, include_header, limit)
            table_node = self.builder.build(table_data, include_header)
            return [table_node]

        except (JsonTableError, FileNotFoundError) as e:
            error_msg = format_error("JsonTable directive error", e)
            logger.error(error_msg)
            return [self._create_error_node(error_msg)]

    def _load_json_data(self) -> JsonData:
        """
        Determine JSON source: file (argument) or inline content.

        Returns:
            Parsed JSON data (object or list).

        Raises:
            JsonTableError: If no JSON source provided.
        """
        if self.arguments:
            return self.loader.load_from_file(
                self.arguments[0],
                Path(self.env.srcdir),
            )
        elif self.content:
            return self.loader.parse_inline(self.content)
        else:
            raise JsonTableError(NO_JSON_SOURCE_ERROR)

    def _create_error_node(self, message: str) -> nodes.Node:
        """
        Create a docutils.error node with the given message.

        Args:
            message: Error message to display in the documentation.

        Returns:
            nodes.error containing a paragraph with the message.
        """
        error_node = nodes.error()
        error_node += nodes.paragraph(text=message)
        return error_node
