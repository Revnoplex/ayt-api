import sys
sys.path.append('../../')
from setup import get_version

# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'AYT API'
copyright = '2024 Revnoplex'
author = 'Revnoplex'

version = get_version('ayt_api/__init__.py')
release = ".".join(version.split(".")[:-1])

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'myst_parser',
    'sphinxext.opengraph',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'notfound.extension'
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'aiohttp': ("https://docs.aiohttp.org/en/stable/", None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'furo'
html_logo = 'https://ayt-api.revnoplex.xyz/ayt-api-square.svg'
html_favicon = html_logo

# -- Options for EPUB output
epub_show_urls = 'footnote'

source_suffix = ['.rst', '.md']
