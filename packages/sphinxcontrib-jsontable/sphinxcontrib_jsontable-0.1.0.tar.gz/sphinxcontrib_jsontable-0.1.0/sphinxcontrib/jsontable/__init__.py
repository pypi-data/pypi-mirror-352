"""
Sphinx extension for rendering JSON data as tables.

This extension provides the jsontable directive that can render JSON data
from external files or inline content as HTML tables in Sphinx documentation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .directives import JsonTableDirective

if TYPE_CHECKING:
    from sphinx.application import Sphinx

__version__ = "0.1.0"
__author__ = "sasakama-code"
__email__ = "sasakamacode@gmail.com"


def setup(app: Sphinx) -> dict[str, Any]:
    """
    Sphinx extension setup function.

    Args:
        app: Sphinx application instance

    Returns:
        Extension metadata
    """
    # Register the jsontable directive
    app.add_directive("jsontable", JsonTableDirective)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
