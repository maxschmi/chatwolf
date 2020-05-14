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
from pathlib import Path
import sphinx_rtd_theme

base_path = Path(os.path.abspath(__file__)).parent.parent.parent
sys.path.insert(0, base_path)
exec(open(str(base_path) + "/doc/Sphinx/create_build.py", "r").read())

# -- Project information -----------------------------------------------------

project = 'Chatwolf'
copyright = '2020, Max Schmit'
author = 'Max Schmit'
author_email = 'maxschm@hotmail.com'

# The full version, including alpha/beta/rc tags
release = '0.1.3'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.napoleon', 
              'recommonmark', 
              'sphinx_rtd_theme',
]

# Add any paths that contain templates here, relative to this directory.
#templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
#exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

#list source file extensions
source_suffix = {
     '.rst': 'restructuredtext',
     '.txt': 'restructuredtext',
     '.md': 'markdown'
}

master_doc = "index"

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"#'alabaster' 

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']

# -- Options for PDF Output --------------------------------------------------
latex_engine = "pdflatex"
#latex_documents = (startdocname = "index")
latex_theme = "manual"