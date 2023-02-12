# Project information
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'flightgear-python'
copyright = '2022, Julianne Swinoga'
author = 'Julianne Swinoga'
release = '1.0.0'

# General configuration
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    'sphinx_mdinclude',
    'sphinx_rtd_theme',
    'sphinx.ext.autosectionlabel',
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

from typing import Any, Tuple, Optional, Callable
from pprint import pformat
from construct import (Struct, FormatField, Subconstruct, Array, Enum, Const, Padded, Pass, Transformed, Flag, Renamed,
                       BitsInteger)
from importlib import import_module
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx import addnodes
from sphinx.util import inspect, logging

logger = logging.getLogger(__name__)


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


def represent_object(o: Any, ident_level: int = 0, context_str: Optional[str] = None) -> Tuple[str, Optional[str]]:
    if isinstance(o, Struct):
        # Print struct members nicely, just a 'wrapper' around dict
        # recurse
        struct_dict = {s.name: s for s in o.subcons}
        val_str, context_str = represent_object(struct_dict, ident_level + 1, context_str)
        pp_str = '\n' + val_str
    elif isinstance(o, dict):
        pp_list = []
        for key, val in o.items():
            # recurse
            val_str, context_str = represent_object(val, ident_level + 1, context_str)
            pp_list.append((' ' * ident_level * 2) + f"'{key}': {val_str}")
        pp_str = '\n'.join(pp_list)
    elif isinstance(o, FormatField):
        pp_str = o.fmtstr
        context_str = 'See Python\'s struct format characters for understanding type sizes'
    elif isinstance(o, Subconstruct):
        if isinstance(o, Array):
            special_str = f'[len={o.count}]'
        elif isinstance(o, Const):
            special_str = f'[val={o.value}]'
        elif isinstance(o, Padded):
            special_str = f'[len={o.length}]'
        elif isinstance(o, Enum):
            # recurse
            val_str, context_str = represent_object(o.ksymapping, ident_level + 1, context_str)
            special_str = f'\n{val_str}\n'
            special_str = special_str.replace('\n', '\n    ')
        elif isinstance(o, Transformed):
            special_str = ''
            # "Transformed" isn't informative, so monkey-patch the type name to show what the underlying type is
            type(o).__name__ = type(o.subcon).__name__
        elif isinstance(o, Renamed):
            special_str = ''
            # "Renamed" isn't informative, so monkey-patch the type name to the "normal" name
            type(o).__name__ = o.name
        else:
            logger.warning(f'No handler for Subconstruct {type(o)} ({o})')
            special_str = ''

        # recurse
        val_str, context_str = represent_object(o.subcon, ident_level + 1, context_str)
        if val_str:
            pp_str = f'{type(o).__name__}{special_str}({val_str})'
        else:
            pp_str = f'{type(o).__name__}{special_str}'
    elif isinstance(o, BitsInteger):
        pp_str = 'Bits'
    elif isinstance(o, Pass.__class__):
        pp_str = ''  # Pass is a do-nothing. No information to represent
    elif isinstance(o, Flag.__class__):
        pp_str = 'Flag'
    elif isinstance(o, Callable):
        pp_str = str(o)  # Maybe could do something better in the future here?
    elif isinstance(o, int):
        pp_str = str(o)
    elif isinstance(o, str):
        pp_str = o
    else:
        logger.warning(f'Default handler for {type(o)} ({o})')
        pp_str = pformat(o, indent=4)

    return pp_str, context_str


class PrintValueDirective(Directive):
    required_arguments = 1

    def run(self):
        module_path, member_name = self.arguments[0].rsplit('.', maxsplit=1)
        obj = getattr(import_module(module_path), member_name)

        if isinstance(obj, Struct):
            type_str = 'Struct with elements'
        elif isinstance(obj, dict):
            type_str = 'dict with elements'
        else:
            type_str = obj.__class__
        pp_str, context_str = represent_object(obj)

        literal = nodes.literal_block(pp_str, pp_str)
        literal['language'] = 'python'

        if context_str is not None:
            text_str = f'{member_name} is {type_str}: ({context_str})'
        else:
            text_str = f'{member_name} is {type_str}:'

        return [addnodes.desc_name(text=text_str),
                addnodes.desc_content('', literal)]


# Automatically called by sphinx at startup
def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip_member_handler)
    app.add_directive('print_val', PrintValueDirective)
