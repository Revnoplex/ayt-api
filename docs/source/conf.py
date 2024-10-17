# Configuration file for the Sphinx documentation builder.
import codecs
import os


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

# -- Project information

project = 'AYT API'
copyright = '2024 Revnoplex'
author = 'Revnoplex'

version = get_version('../../ayt_api/__init__.py')
release = ".".join(version.split(".")[:-1])

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
