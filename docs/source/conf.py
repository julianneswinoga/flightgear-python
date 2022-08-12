# Project information
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'flightgear-python'
copyright = '2022, Julianne Swinoga'
author = 'Julianne Swinoga'
release = '1.0.0'

# General configuration
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]
autodoc_typehints = 'description'
autosummary_generate = True

intersphinx_mapping = {
    'python': ('http://docs.python.org/3', None),
}

templates_path = ['_templates']
exclude_patterns = []

# HTML configuration
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']


from pprint import pformat

from construct import Struct
from importlib import import_module
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx import addnodes
from sphinx.util import inspect


def object_description(obj) -> str:
    max_len = 50  # limit to 50 chars
    obj_str = orig_inspect_object_description(obj)
    if len(obj_str) <= max_len:
        return obj_str
    return obj_str[:max_len - 10] + ' ... ' + obj_str[-5:]


# monkey-patch how sphinx represents values
orig_inspect_object_description = inspect.object_description
inspect.object_description = object_description


# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#event-autodoc-skip-member
def autodoc_skip_member_handler(app, what, name, obj, skip, options):
    docstr = obj.__doc__
    if docstr:
        should_skip = 'sphinx-no-autodoc' in docstr
    else:
        should_skip = False
    if name.startswith('_'):  # Always skip private objects
        should_skip = True
    return should_skip


class PrintValueDirective(Directive):
    required_arguments = 1

    def run(self):
        module_path, member_name = self.arguments[0].rsplit('.', maxsplit=1)
        obj = getattr(import_module(module_path), member_name)

        if isinstance(obj, Struct):
            # Print struct members nicely
            keys = [s.name for s in obj.subcons]
            pp_str = '\n'.join(keys)
        else:
            pp_str = pformat(obj, indent=4)

        literal = nodes.literal_block(pp_str, pp_str)
        literal['language'] = 'python'

        return [addnodes.desc_name(text=f'{member_name} is defined as:'),
                addnodes.desc_content('', literal)]


# Automatically called by sphinx at startup
def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip_member_handler)
    app.add_directive('print_val', PrintValueDirective)
