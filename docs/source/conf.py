# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'AYT API'
copyright = '2024 Revnoplex'
author = 'Revnoplex'

release = '0.3'
version = '0.3.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'myst_parser',
    'sphinx_rtd_dark_mode',
    'sphinxext.opengraph'
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'
html_logo = 'https://ayt-api.revnoplex.xyz/ayt-api-square.svg'
html_favicon = html_logo

# -- Options for EPUB output
epub_show_urls = 'footnote'

source_suffix = ['.rst', '.md']
