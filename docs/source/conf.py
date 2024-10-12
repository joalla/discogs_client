# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../../discogs_client/'))


# -- Project information -----------------------------------------------------

project = 'python3-discogs-client'
copyright = '2020-2024, The Joalla Team'
author = 'The Joalla Team'

# The full version, including alpha/beta/rc tags
release = '2.7'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'myst_parser',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

html_last_updated_fmt = "%b %d, %Y"
html_logo = '_static/discogs-vinyl-record-mark-50x50.png'
html_context = {
    "github_user": "joalla",
    "github_repo": "discogs_client",
    "github_version": "master",
    "doc_path": "docs/source/",
}
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/joalla/discogs_client",
            "icon": "fa-brands fa-github",
        },
    ],
    "use_edit_page_button": True,
    "header_links_before_dropdown": 3,
    "show_toc_level": 5,
    "back_to_top_button": False,
}
html_title = ""
html_static_path = ["_static"]
html_css_files = ["p3dc.css"]

# MyST extenstion configuration
myst_heading_anchors = 7
myst_enable_extensions = [
    "substitution"
]
myst_substitutions = {
  "class": "I'm a **substitution**"
}

# -- autodoc tuning -------------------------------------------------
# don't show docstring of parent classes on childs
autodoc_inherit_docstrings = False

# show docstring of class AND __init__ method
autoclass_content = 'both'

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'private-members': True,
    'member-order': 'bysource',
}
