# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

# Must be imported after the parent directory was added to sys.path for global sphinx installation.
import factory  # noqa

# -- Project information -----------------------------------------------------

project = 'Factory Boy'
copyright = '2011-2015, Raphaël Barrois, Mark Sandstrom'
author = 'Raphaël Barrois, Mark Sandstrom'

# The full version, including alpha/beta/rc tags
release = factory.__version__
# The short X.Y version.
version = '.'.join(release.split('.')[:2])

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

extlinks = {
    'issue': ('https://github.com/FactoryBoy/factory_boy/issues/%s', 'issue %s'),
    'pr': ('https://github.com/FactoryBoy/factory_boy/pull/%s', 'pull request %s'),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

if 'READTHEDOCS_VERSION' in os.environ:
    # Use the readthedocs version string in preference to our known version.
    html_title = "{} {} documentation".format(
        project, os.environ['READTHEDOCS_VERSION'])

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- linkcheck ---------------------------------------------------------------
linkcheck_retries = 3


# -- intersphinx -------------------------------------------------------------
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'django': (
        'https://docs.djangoproject.com/en/dev/',
        'https://docs.djangoproject.com/en/dev/_objects/',
    ),
    'mongoengine': (
        'https://mongoengine-odm.readthedocs.io/',
        None,
    ),
    'sqlalchemy': (
        'https://docs.sqlalchemy.org/en/latest/',
        'https://docs.sqlalchemy.org/en/latest/objects.inv',
    ),
}


# -- spelling ---------------------------------------------------------------
spelling_exclude_patterns = [
    'credits.rst',
]
