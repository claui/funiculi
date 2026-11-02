# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# pylint: skip-file
# type: ignore

project = 'Funiculi'
executable = 'funiculi'
author = 'Claudia Pellegrino <clau@tiqua.de>'
description = 'Control your Denon AVR amplifier from the command line'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'autoapi.extension',
    'myst_parser',
    'sphinx.ext.autodoc',
]

autoapi_dirs = ['../../funiculi']
autoapi_keep_files = True
autoapi_ignore = ['**/stubs/**']
autoapi_options = [
    'members',
    'undoc-members',
    'show-inheritance',
    'show-module-summary',
    'special-members',
    'imported-members',
]
autoapi_type = 'python'
autodoc_typehints = 'description'

html_theme = 'sphinx_rtd_theme'

myst_enable_extensions = [
    'deflist',
]


def skip_module(app, what, name, obj, skip, options):
    if what != 'module':
        return skip
    if name in [
        'funiculi.__main__',
        'funiculi.cli',
        'funiculi.config',
        'funiculi.fire_workarounds',
        'funiculi.settings',
        'funiculi.version',
    ]:
        return True
    return skip


def setup(sphinx):
    sphinx.connect('autoapi-skip-member', skip_module)


templates_path = []
exclude_patterns = [
    '**/funiculi/__main__/**',
    '**/funiculi/cli/**',
    '**/funiculi/config/**',
    '**/funiculi/fire_workarounds/**',
    '**/funiculi/settings/**',
    '**/funiculi/version/**',
]

# Man page output

man_pages = [
    (
        'usage',
        executable,
        description,
        [author],
        1,
    )
]

man_show_urls = True
