# -*- coding: utf-8 -*-

# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import os
import sublime

from suricate import build_variables
from suricate import import_module

process = import_module('lib.process')
sublime_wrapper = import_module('lib.sublime_wrapper')

def clean(view=None):
    """Remove LaTeX temporary files."""
    temp_extensions = ['.log', '.aux', '.dvi', '.lof', '.lot', '.bit', '.idx',
                       '.glo', '.bbl', '.ilg', '.toc', '.ind', '.out',
                       '.synctex.gz', '.blg']
    bvars = build_variables.get(view)
    prefix = os.path.abspath(os.path.join(bvars['file_path'], bvars['file_base_name']))
    counter = 0
    for path in map(lambda ext: prefix + ext, temp_extensions):
      if os.access(path, os.F_OK):
        os.remove(path)
        counter += 1
    sublime.status_message('%i files removed' % counter)

def launchpdf(view=None):
    """Launch pdf associated with view."""
    bvars = build_variables.get(view)
    prefix = os.path.abspath(os.path.join(bvars['file_path'], bvars['file_base_name']))
    process.start_file(prefix + '.pdf')

def convert_to_tex(string):
    """Convert special characters to TeX symbols."""
    for char, tex in Map:
      string = string.replace(char, tex)
    return string

def paragraph_to_tex(edit, view):
    """Convert special characters in paragraph to TeX symbols."""
    view.run_command('expand_selection_to_paragraph')
    func = lambda region: convert_to_tex(view.substr(region))
    sublime_wrapper.foreach_region(func, edit, view, clear=True)

Map = [
    ('#', r'\#'),
    ('%', r'\%'),
    ('&', r'\&'),
    ('~', r'~'),
    ('¡', r'!`'),
    ('¿', r'?`'),
    ('À', r'\`A'),
    ('Á', r'\'A'),
    ('Ä', r'\"A'),
    ('Ç', r'\c{C}'),
    ('È', r'\`E'),
    ('É', r'\'E'),
    ('Ë', r'\"E'),
    ('Ì', r'\`I'),
    ('Í', r'\'I'),
    ('Ï', r'\"I'),
    ('Ñ', r'\~N'),
    ('Ò', r'\`O'),
    ('Ó', r'\'O'),
    ('Ö', r'\"O'),
    ('Ù', r'\`U'),
    ('Ú', r'\'U'),
    ('Ü', r'\"U'),
    ('à', r'\`a'),
    ('á', r'\'a'),
    ('ä', r'\"a'),
    ('ç', r'\c{c}'),
    ('è', r'\`e'),
    ('é', r'\'e'),
    ('ë', r'\"e'),
    ('ì', r'\`i'),
    ('í', r'\'i'),
    ('ï', r'\"i'),
    ('ñ', r'\~n'),
    ('ò', r'\`o'),
    ('ó', r'\'o'),
    ('ö', r'\"o'),
    ('ù', r'\`u'),
    ('ú', r'\'u'),
    ('ü', r'\"u'),
]
