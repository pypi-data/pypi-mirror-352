import os
import sys

sys.path.insert(0, os.path.abspath(".."))


"""
Sphinx configuration file for examples.
"""

# Configuration file for the Sphinx documentation builder.

project = "sphinxcontrib-jsontable Examples"
copyright = "%Y, sasakama-code"
author = "sasakama-code"

# The full version, including alpha/beta/rc tags
release = "0.1.0"

# Add any Sphinx extension module names here
extensions = [
    "sphinxcontrib.jsontable",
    "myst_parser",  # For MyST Markdown support
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The theme to use for HTML and HTML Help pages.
html_theme = "alabaster"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# MyST configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
]

# Source file suffixes
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}
