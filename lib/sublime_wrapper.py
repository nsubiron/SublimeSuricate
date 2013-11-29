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

"""Handy wrappers around sublime API."""

import os
import sublime

from suricate import build_variables

def execute(**kwargs):
    """Runs an external process asynchronously. On Windows, GUIs are suppressed.
    ``exec`` is the default command used by build systems, thus it provides
    similar functionality. However, a few options in build systems are taken
    care of by Sublime Text internally so they list below only contains
    parameters accepted by this command.
      * cmd ``[String]``
      * file_regex ``String``
      * line_regex ``String``
      * working_dir ``String``
      * encoding ``String``
      * env ``{String: String}``
      * path ``String``
      * shell ``Bool``
      * kill ``Bool``: If True will simply terminate the current build process.
      This is invoked via Build: Cancel command from the Command Palette.
      * quiet ``Bool``: If True prints less information about running the
      command."""
    window = sublime.active_window()
    window.run_command('exec', build_variables.expand(kwargs, window.active_view()))

def flush_to_buffer(text, name=None, scratch=False, syntax=None, syntax_file=None):
    """Flush text to a new buffer."""
    view = sublime.active_window().new_file()
    view.set_scratch(scratch)
    if name is not None:
      view.set_name(name)
    if syntax is not None:
      view.set_syntax_file('Packages/{0}/{0}.tmLanguage'.format(syntax))
    elif syntax_file is not None:
      view.set_syntax_file(syntax_file)
    edit = view.begin_edit()
    view.insert(edit, 0, text)
    view.end_edit(edit)

def show_quick_panel(display_list, on_done, window=None):
    """Show a quick panel fed with display_list on window. on_done must be a
    callable object that accepts one argument, the element picked (not the
    index!). It won't be called if the user cancels."""
    if not display_list:
      print('Quick panel fed with an empty list!')
      return
    if window is None:
      window = sublime.active_window()
    def _on_done(index):
        if index != -1:
          return on_done(display_list[index])
        sublime.status_message('Cancelled')
    window.run_command('hide_overlay')
    window.show_quick_panel(display_list, _on_done)

def copy_build_variable_to_clipboard(key=None):
    """If key is None, show a quick panel with the currently available build
    variables."""
    vmap = build_variables.get()
    on_done = lambda picked: sublime.set_clipboard(picked[1])
    if key is None:
      show_quick_panel(sorted([[k,i] for k, i in vmap.items()]), on_done)
    else:
      on_done([None, vmap[key]])

def paste_build_variable(key=None, view=None):
    """If key is None, show a quick panel with the currently available build
    variables."""
    vmap = build_variables.get()
    on_done = lambda picked: insert(picked[1], view, clear=True)
    if key is None:
      show_quick_panel(sorted([[k,i] for k, i in vmap.items()]), on_done)
    else:
      on_done([None, vmap[key]])

def get_selection(view=None):
    """Retrieve selected regions as a list of strings."""
    if view is None:
      view = sublime.active_window().active_view()
    return [view.substr(region) for region in view.sel()]

def insert(string, view=None, clear=False):
    """Insert string replacing view's current selection. If clear, move the
    cursor to the end of each region."""
    if view is None:
      view = sublime.active_window().active_view()
    edit = view.begin_edit()
    for region in view.sel():
      if clear:
        view.replace(edit, region, '')
        view.insert(edit, region.begin(), string)
      else:
        view.replace(edit, region, string)
    view.end_edit(edit)

def foreach_region(func, view=None, clear=False):
    """Replace each selected region by the result of applying func on that
    region. If clear, move the cursor to the end of each region."""
    if view is None:
      view = sublime.active_window().active_view()
    edit = view.begin_edit()
    for region in view.sel():
      string = func(region)
      if clear:
        view.replace(edit, region, '')
        view.insert(edit, region.begin(), string)
      else:
        view.replace(edit, region, string)
    view.end_edit(edit)
