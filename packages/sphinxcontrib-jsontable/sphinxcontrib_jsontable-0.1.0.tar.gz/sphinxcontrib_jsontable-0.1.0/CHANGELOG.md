# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Planned features for future releases

### Changed
- Planned improvements for future releases

### Fixed
- Planned bug fixes for future releases

## [0.1.0] - 2025-06-02

### Added
- Initial release of sphinxcontrib-jsontable
- Support for JSON files and inline content rendering as tables
- `header` option to include first row as table header
- `encoding` option for custom file encoding (default: utf-8)
- `limit` option to restrict number of rows displayed
- Support for multiple JSON data formats:
  - Arrays of objects (with automatic header extraction from keys)
  - 2D arrays (with optional header row)
  - Single objects (key-value pairs)
  - Mixed data types with safe string conversion
- Comprehensive error handling and validation
- Path traversal protection for security
- Safe file access within Sphinx source directory only
- Detailed logging for debugging
- Full integration with both reStructuredText and MyST Markdown
- Complete documentation with examples and best practices

### Security
- Implemented path traversal protection
- File access restricted to Sphinx source directory
- Input validation for all directive options
- Safe JSON parsing with error handling

### Performance
- Efficient JSON loading and parsing
- Memory-conscious handling of large datasets
- Optional row limiting for performance optimization

### Changed
- **BREAKING**: Minimum Python version raised to 3.10+
- **BREAKING**: Dropped support for Python 3.9 and earlier versions
- Updated build system to use modern Python packaging standards
- Improved code quality with ruff and mypy integration

---

## Release Notes

### v0.1.0 - Initial Release

This is the first stable release of sphinxcontrib-jsontable, providing a robust solution for embedding JSON data as tables in Sphinx documentation.

**Key Features:**
- 🚀 Easy integration with existing Sphinx projects
- 📊 Multiple data format support
- 🛡️ Security-first design with path protection
- 📝 Comprehensive documentation and examples
- 🔧 Flexible customization options

**Compatibility:**
- Python 3.10+ (3.10, 3.11, 3.12)
- Sphinx 3.0+
- Docutils 0.18+

**Installation:**
```bash
pip install sphinxcontrib-jsontable
```

**Quick Start:**
```rst
.. jsontable:: data/example.json
   :header:
   :limit: 10
```

For detailed usage instructions, see [README.md](README.md).

---

## Migration Guide

### Python Version Requirements

**Important:** This package requires Python 3.10 or later. If you're using an older Python version:

1. **Upgrade Python**: Install Python 3.10+ on your system
2. **Virtual Environment**: Create a new virtual environment with the supported Python version
3. **Dependencies**: Ensure all your project dependencies are compatible with Python 3.10+

### From Custom Solutions

If you're currently using custom scripts or other methods to generate tables from JSON:

1. **Export your data to JSON format** if not already in JSON
2. **Replace custom table generation** with `.. jsontable::` directive
3. **Update file paths** to be relative to your Sphinx source directory
4. **Add appropriate options** (`:header:`, `:limit:`, etc.) based on your needs

### From Other Extensions

**From sphinx-jsonschema:**
- Replace `.. jsonschema::` with `.. jsontable::`
- Remove schema validation options (not applicable)
- Add `:header:` option if you want column headers

**From manual table creation:**
- Replace manual reStructuredText tables with `.. jsontable::` directive
- Move your data to JSON files for easier maintenance
- Leverage automatic header extraction for object arrays

---

## Contributing to Changelog

When contributing to this project, please:

1. **Add entries to the Unreleased section** for new features, changes, or fixes
2. **Follow the format** specified in Keep a Changelog
3. **Include appropriate subsections** (Added, Changed, Deprecated, Removed, Fixed, Security)
4. **Be descriptive** but concise in your entries
5. **Include issue/PR references** where applicable

Example entry format:
```markdown
### Added
- New `custom-option` directive option for advanced formatting (#123)
- Support for YAML input in addition to JSON (#145)

### Fixed
- Resolved encoding issue with non-ASCII characters in file paths (#134)
```

---

*For the latest updates and detailed release information, see the [GitHub Releases](https://github.com/sasakama-code/sphinxcontrib-jsontable/releases) page.*
