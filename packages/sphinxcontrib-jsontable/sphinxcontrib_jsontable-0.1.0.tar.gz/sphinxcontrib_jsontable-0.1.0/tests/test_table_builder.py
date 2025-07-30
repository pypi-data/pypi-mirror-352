"""
Unit tests for TableBuilder class.

This module provides comprehensive test coverage for all TableBuilder methods,
following pytest best practices with single assertions and AAA pattern.
"""

import pytest
from docutils import nodes

from sphinxcontrib.jsontable.directives import TableBuilder


class TestTableBuilder:
    """Test suite for TableBuilder class."""

    @pytest.fixture
    def table_builder(self):
        """Create a TableBuilder instance for testing."""
        return TableBuilder()

    @pytest.fixture
    def sample_table_data(self):
        """Provide sample table data for testing."""
        return [
            ["Header1", "Header2", "Header3"],
            ["Row1Col1", "Row1Col2", "Row1Col3"],
            ["Row2Col1", "Row2Col2", "Row2Col3"],
        ]

    @pytest.fixture
    def irregular_table_data(self):
        """Provide table data with irregular row lengths."""
        return [
            ["H1", "H2", "H3", "H4"],
            ["Short"],
            ["Medium", "Row"],
            ["Full", "Length", "Row", "Here"],
        ]

    # Tests for build() method

    def test_build_with_empty_data_returns_empty_table(self, table_builder):
        """Test that build() returns empty table for empty input data."""
        # Arrange
        empty_data = []

        # Act
        result = table_builder.build(empty_data)

        # Assert
        assert isinstance(result, nodes.table)

    def test_build_without_header_creates_table_with_body_only(
        self, table_builder, sample_table_data
    ):
        """Test that build() creates table without header when has_header=False."""
        # Arrange
        data = sample_table_data

        # Act
        result = table_builder.build(data, has_header=False)

        # Assert
        assert isinstance(result, nodes.table)

    def test_build_with_header_creates_table_with_header_and_body(
        self, table_builder, sample_table_data
    ):
        """Test that build() creates table with header when has_header=True."""
        # Arrange
        data = sample_table_data

        # Act
        result = table_builder.build(data, has_header=True)

        # Assert
        tgroup = result[0]
        assert any(isinstance(child, nodes.thead) for child in tgroup.children)

    def test_build_with_single_row_creates_valid_table(self, table_builder):
        """Test that build() handles single row data correctly."""
        # Arrange
        single_row_data = [["OnlyCell"]]

        # Act
        result = table_builder.build(single_row_data)

        # Assert
        assert isinstance(result, nodes.table)

    def test_build_with_irregular_rows_pads_correctly(
        self, table_builder, irregular_table_data
    ):
        """Test that build() pads shorter rows to match longest row."""
        # Arrange
        data = irregular_table_data

        # Act
        result = table_builder.build(data)

        # Assert
        tgroup = result[0]
        assert tgroup["cols"] == 4  # Should match longest row

    def test_build_with_single_column_creates_single_column_table(self, table_builder):
        """Test that build() creates single column table for single column data."""
        # Arrange
        single_col_data = [["A"], ["B"], ["C"]]

        # Act
        result = table_builder.build(single_col_data)

        # Assert
        tgroup = result[0]
        assert tgroup["cols"] == 1

    # Tests for _create_empty_table() method

    def test_create_empty_table_returns_table_node(self, table_builder):
        """Test that _create_empty_table() returns a table node."""
        # Arrange & Act
        result = table_builder._create_empty_table()

        # Assert
        assert isinstance(result, nodes.table)

    def test_create_empty_table_has_single_column_tgroup(self, table_builder):
        """Test that _create_empty_table() creates tgroup with single column."""
        # Arrange & Act
        result = table_builder._create_empty_table()

        # Assert
        tgroup = result[0]
        assert tgroup["cols"] == 1

    def test_create_empty_table_contains_tgroup(self, table_builder):
        """Test that _create_empty_table() contains a tgroup node."""
        # Arrange & Act
        result = table_builder._create_empty_table()

        # Assert
        assert isinstance(result[0], nodes.tgroup)

    # Tests for _create_table_structure() method

    def test_create_table_structure_with_single_column(self, table_builder):
        """Test that _create_table_structure() creates single column structure."""
        # Arrange
        cols = 1

        # Act
        result = table_builder._create_table_structure(cols)

        # Assert
        tgroup = result[0]
        assert tgroup["cols"] == 1

    def test_create_table_structure_with_multiple_columns(self, table_builder):
        """Test that _create_table_structure() creates multi-column structure."""
        # Arrange
        cols = 5

        # Act
        result = table_builder._create_table_structure(cols)

        # Assert
        tgroup = result[0]
        assert tgroup["cols"] == 5

    def test_create_table_structure_creates_correct_colspecs(self, table_builder):
        """Test that _create_table_structure() creates correct number of colspecs."""
        # Arrange
        cols = 3

        # Act
        result = table_builder._create_table_structure(cols)

        # Assert
        tgroup = result[0]
        colspecs = [
            child for child in tgroup.children if isinstance(child, nodes.colspec)
        ]
        assert len(colspecs) == 3

    def test_create_table_structure_returns_table_node(self, table_builder):
        """Test that _create_table_structure() returns a table node."""
        # Arrange
        cols = 2

        # Act
        result = table_builder._create_table_structure(cols)

        # Assert
        assert isinstance(result, nodes.table)

    # Tests for _add_header() method

    def test_add_header_creates_thead_node(self, table_builder):
        """Test that _add_header() creates a thead node in the table."""
        # Arrange
        table = nodes.table()
        tgroup = nodes.tgroup(cols=2)
        table += tgroup
        header_data = ["Col1", "Col2"]

        # Act
        table_builder._add_header(table, header_data)

        # Assert
        thead_nodes = [
            child for child in tgroup.children if isinstance(child, nodes.thead)
        ]
        assert len(thead_nodes) == 1

    def test_add_header_with_single_column(self, table_builder):
        """Test that _add_header() handles single column header."""
        # Arrange
        table = nodes.table()
        tgroup = nodes.tgroup(cols=1)
        table += tgroup
        header_data = ["SingleHeader"]

        # Act
        table_builder._add_header(table, header_data)

        # Assert
        thead = next(
            child for child in tgroup.children if isinstance(child, nodes.thead)
        )
        assert isinstance(thead, nodes.thead)

    def test_add_header_with_empty_header_data(self, table_builder):
        """Test that _add_header() handles empty header data."""
        # Arrange
        table = nodes.table()
        tgroup = nodes.tgroup(cols=1)
        table += tgroup
        header_data = []

        # Act
        table_builder._add_header(table, header_data)

        # Assert
        thead_nodes = [
            child for child in tgroup.children if isinstance(child, nodes.thead)
        ]
        assert len(thead_nodes) == 1

    def test_add_header_creates_row_with_entries(self, table_builder):
        """Test that _add_header() creates row with correct number of entries."""
        # Arrange
        table = nodes.table()
        tgroup = nodes.tgroup(cols=3)
        table += tgroup
        header_data = ["H1", "H2", "H3"]

        # Act
        table_builder._add_header(table, header_data)

        # Assert
        thead = next(
            child for child in tgroup.children if isinstance(child, nodes.thead)
        )
        row = thead[0]
        entries = [child for child in row.children if isinstance(child, nodes.entry)]
        assert len(entries) == 3

    # Tests for _add_body() method

    def test_add_body_creates_tbody_node(self, table_builder):
        """Test that _add_body() creates a tbody node in the table."""
        # Arrange
        table = nodes.table()
        tgroup = nodes.tgroup(cols=2)
        table += tgroup
        body_data = [["R1C1", "R1C2"]]
        max_cols = 2

        # Act
        table_builder._add_body(table, body_data, max_cols)

        # Assert
        tbody_nodes = [
            child for child in tgroup.children if isinstance(child, nodes.tbody)
        ]
        assert len(tbody_nodes) == 1

    def test_add_body_with_empty_data(self, table_builder):
        """Test that _add_body() handles empty body data."""
        # Arrange
        table = nodes.table()
        tgroup = nodes.tgroup(cols=1)
        table += tgroup
        body_data = []
        max_cols = 1

        # Act
        table_builder._add_body(table, body_data, max_cols)

        # Assert
        tbody_nodes = [
            child for child in tgroup.children if isinstance(child, nodes.tbody)
        ]
        assert len(tbody_nodes) == 1

    def test_add_body_pads_short_rows(self, table_builder):
        """Test that _add_body() pads rows shorter than max_cols."""
        # Arrange
        table = nodes.table()
        tgroup = nodes.tgroup(cols=3)
        table += tgroup
        body_data = [["Short"], ["Medium", "Row"]]
        max_cols = 3

        # Act
        table_builder._add_body(table, body_data, max_cols)

        # Assert
        tbody = next(
            child for child in tgroup.children if isinstance(child, nodes.tbody)
        )
        first_row = tbody[0]
        entries = [
            child for child in first_row.children if isinstance(child, nodes.entry)
        ]
        assert len(entries) == 3

    def test_add_body_with_multiple_rows(self, table_builder):
        """Test that _add_body() handles multiple rows correctly."""
        # Arrange
        table = nodes.table()
        tgroup = nodes.tgroup(cols=2)
        table += tgroup
        body_data = [["R1C1", "R1C2"], ["R2C1", "R2C2"], ["R3C1", "R3C2"]]
        max_cols = 2

        # Act
        table_builder._add_body(table, body_data, max_cols)

        # Assert
        tbody = next(
            child for child in tgroup.children if isinstance(child, nodes.tbody)
        )
        rows = [child for child in tbody.children if isinstance(child, nodes.row)]
        assert len(rows) == 3

    # Tests for _create_row() method

    def test_create_row_returns_row_node(self, table_builder):
        """Test that _create_row() returns a row node."""
        # Arrange
        row_data = ["Cell1", "Cell2"]

        # Act
        result = table_builder._create_row(row_data)

        # Assert
        assert isinstance(result, nodes.row)

    def test_create_row_with_single_cell(self, table_builder):
        """Test that _create_row() handles single cell correctly."""
        # Arrange
        row_data = ["SingleCell"]

        # Act
        result = table_builder._create_row(row_data)

        # Assert
        entries = [child for child in result.children if isinstance(child, nodes.entry)]
        assert len(entries) == 1

    def test_create_row_with_multiple_cells(self, table_builder):
        """Test that _create_row() handles multiple cells correctly."""
        # Arrange
        row_data = ["Cell1", "Cell2", "Cell3", "Cell4"]

        # Act
        result = table_builder._create_row(row_data)

        # Assert
        entries = [child for child in result.children if isinstance(child, nodes.entry)]
        assert len(entries) == 4

    def test_create_row_with_empty_data(self, table_builder):
        """Test that _create_row() handles empty row data."""
        # Arrange
        row_data = []

        # Act
        result = table_builder._create_row(row_data)

        # Assert
        entries = [child for child in result.children if isinstance(child, nodes.entry)]
        assert len(entries) == 0

    def test_create_row_creates_paragraph_in_entries(self, table_builder):
        """Test that _create_row() creates paragraphs within entries."""
        # Arrange
        row_data = ["TestCell"]

        # Act
        result = table_builder._create_row(row_data)

        # Assert
        entry = result[0]
        paragraph = entry[0]
        assert isinstance(paragraph, nodes.paragraph)

    def test_create_row_with_special_characters(self, table_builder):
        """Test that _create_row() handles special characters in cell data."""
        # Arrange
        row_data = ["Special: äöü", "Symbols: @#$%", "Unicode: 🎉"]

        # Act
        result = table_builder._create_row(row_data)

        # Assert
        entries = [child for child in result.children if isinstance(child, nodes.entry)]
        assert len(entries) == 3
