# -*- coding: utf-8 -*-

# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import os

import sublime

import suricate

from . import process
from . import sublime_wrapper

suricate.reload_module(process)
suricate.reload_module(sublime_wrapper)


def _get_path_prefix(window):
    variables = suricate.extract_variables(window)
    return os.path.abspath(
        os.path.join(
            variables['file_path'],
            variables['file_base_name']))


def clean(window=None):
    """Remove LaTeX temporary files."""
    temp_extensions = ['.log', '.aux', '.dvi', '.lof', '.lot', '.bit', '.idx',
                       '.glo', '.bbl', '.ilg', '.toc', '.ind', '.out',
                       '.synctex.gz', '.blg']
    prefix = _get_path_prefix(window)
    counter = 0
    for path in [prefix + ext for ext in temp_extensions]:
        if os.access(path, os.F_OK):
            os.remove(path)
            counter += 1
    message = '%i files removed' % counter
    suricate.log(message)
    sublime.status_message(message)


def launch_pdf(window=None):
    """Launch PDF associated with view."""
    process.startfile(_get_path_prefix(window) + '.pdf')


def convert_to_tex(string):
    """Convert special characters to TeX symbols."""
    # @todo add more symbols
    tex_symbols = sublime_wrapper.locate_and_load_resource('tex_symbols_map')
    if not tex_symbols:
        suricate.log('ERROR: unable to load \'tex_symbols_map\'')
        return
    for char, tex in [x.split(' ') for x in tex_symbols.splitlines()]:
        string = string.replace(char, tex)
    return string


def paragraph_to_tex(edit, view):
    """Convert special characters in paragraph to TeX symbols."""
    view.run_command('expand_selection_to_paragraph')
    func = lambda region: convert_to_tex(view.substr(region))
    sublime_wrapper.foreach_region(func, edit, view, clear=True)
