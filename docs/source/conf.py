# Project information
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'flightgear-python'
copyright = '2022, Julianne Swinoga'
author = 'Julianne Swinoga'
release = '1.0.0'

# General configuration
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    'autoapi.extension',
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc',
]

templates_path = ['_templates']
exclude_patterns = []

# autoapi configuration
autoapi_dirs = ['../../flightgear_python']
autoapi_options = [
    'members',
    'undoc-members',
    # 'private-members',
    'show-inheritance',
    'show-module-summary',
    'special-members',
    'imported-members',
    'inherited-members',
]
autodoc_typehints = 'description'

# HTML configuration
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


def autoapi_skip_member_handler(app, what, name, obj, skip, options):
    if obj.docstring:
        should_skip = 'sphinx-no-autoapi' in obj.docstring
    else:
        should_skip = False
    print(name, should_skip)
    return should_skip


# Automatically called by sphinx at startup
def setup(app):
    # Connect the autoapi-skip-member event from apidoc to the callback
    app.connect('autoapi-skip-member', autoapi_skip_member_handler)

