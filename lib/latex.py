# -*- coding: utf-8 -*-

# Sublime Suricate is licensed under the GPL license.
#
# Copyright (C) 2013 N. Subiron
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import os
import sublime

if sublime.version() >= '3000':
  raise Exception('Not implemented for this platform.')

temp_extensions = ['.log', '.aux', '.dvi', '.lof', '.lot', '.bit', '.idx',
                   '.glo', '.bbl', '.ilg', '.toc', '.ind', '.out',
                   '.synctex.gz', '.blg']

def clean(view=None):
    """Remove LaTeX temporary files."""
    bvars = sublime_wrapper.get_build_variables(view)
    prefix = os.path.abspath(os.path.join(bvars['file_path'], bvars['file_base_name']))
    counter = 0
    for path in map(lambda ext: prefix + ext, temp_extensions):
      if os.access(path, os.F_OK):
        os.remove(path)
        counter += 1
    sublime.status_message('%i files removed' % counter)

def launchpdf(view=None):
    """Launch pdf associated with view."""
    bvars = sublime_wrapper.get_build_variables(view)
    prefix = os.path.abspath(os.path.join(bvars['file_path'], bvars['file_base_name']))
    process.start_file(prefix + '.pdf')

def convert_to_tex(string):
    """Convert special characters to TeX symbols."""
    for char, tex in Map:
      string = string.replace(char, tex)
    return string

def paragraph_to_tex(view):
    """Convert special characters in paragraph to TeX symbols."""
    view.run_command('expand_selection_to_paragraph')
    func = lambda region: convert_to_tex(view.substr(region))
    sublime_wrapper.foreach_region(func, view, clear=True)

_P = lambda char, tex: (unicode(char, 'utf-8'), tex)

Map = [
    _P('#', r'\#'),
    _P('%', r'\%'),
    _P('&', r'\&'),
    _P('~', r'~'),
    _P('¡', r'!`'),
    _P('¿', r'?`'),
    _P('À', r'\`A'),
    _P('Á', r'\'A'),
    _P('Ä', r'\"A'),
    _P('Ç', r'\c{C}'),
    _P('È', r'\`E'),
    _P('É', r'\'E'),
    _P('Ë', r'\"E'),
    _P('Ì', r'\`I'),
    _P('Í', r'\'I'),
    _P('Ï', r'\"I'),
    _P('Ñ', r'\~N'),
    _P('Ò', r'\`O'),
    _P('Ó', r'\'O'),
    _P('Ö', r'\"O'),
    _P('Ù', r'\`U'),
    _P('Ú', r'\'U'),
    _P('Ü', r'\"U'),
    _P('à', r'\`a'),
    _P('á', r'\'a'),
    _P('ä', r'\"a'),
    _P('ç', r'\c{c}'),
    _P('è', r'\`e'),
    _P('é', r'\'e'),
    _P('ë', r'\"e'),
    _P('ì', r'\`i'),
    _P('í', r'\'i'),
    _P('ï', r'\"i'),
    _P('ñ', r'\~n'),
    _P('ò', r'\`o'),
    _P('ó', r'\'o'),
    _P('ö', r'\"o'),
    _P('ù', r'\`u'),
    _P('ú', r'\'u'),
    _P('ü', r'\"u'),
]
