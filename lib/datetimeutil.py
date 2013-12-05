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

import sublime

from datetime import datetime
from suricate import Settings
from suricate import import_module

sublime_wrapper = import_module('lib.sublime_wrapper')

def _datetime_formats():
    defaults = ['%Y:%m:%d', '%Y/%m/%d', '%d/%m/%Y', '%d %B %Y', '%A, %B %d, %Y',
                '%Y%m%d', '%Y%m%d%H%M%S', '%a %d', '%c', 'Week %W, day %j',
                '%H:%M:%S', '%H:%M', '%Y']
    return Settings.get('time_formats', defaults)

def get_times(tstring=None, quiet=False):
    """Return a list of the different formats available for tstring, see
    "time_formats" on settings file. If tstring is None, use current
    time."""
    formats = _datetime_formats()
    if tstring is None:
      time = datetime.now()
    else:# 11/21/13 14:00:44
      time, _ = _read_time(tstring, formats, quiet)
    if time is None:
      return None
    return [ time.strftime(format) for format in formats ]

def _read_time(tstring, tformats, quiet=False):
    """Try to convert tstring to a format in tformats, return first
    match. If non of them matches, show an error message."""
    for format in tformats:
      try:
        return datetime.strptime(str(tstring), format), format
      except ValueError:
        pass
    if not quiet:
      msg = 'Unknown time format: "%s"\nSee "time_formats" in settings file.'
      sublime.error_message(string % tstring)
    return None, None

def time_to_clipboard(view=None):
    regions = sublime_wrapper.get_selection(view)
    tformats = _datetime_formats()
    for selection in regions + [None]:
      times = get_times(selection, tformats)
      if times is not None:
        break
    on_done = lambda picked: sublime.set_clipboard(picked)
    sublime_wrapper.show_quick_panel(times, on_done)

def continue_serie(edit, view):
    # @todo Improve. Fails for one year increments on leap-years.
    selection = sublime_wrapper.get_selection(view)[0]
    # Use just last two lines.
    lines = selection.split('\n')
    while not lines[-1]:
      lines = lines[:-1]
    if len(lines) < 2 or not lines[-2] or not lines[-1]:
      return
    # Use indentation and format of the second line.
    indentation = 0
    while lines[-1][indentation] == ' ':
      indentation += 1
    formats = _datetime_formats()
    time0, format = _read_time(lines[-2].strip(), formats)
    time1, format = _read_time(lines[-1].strip(), formats)
    if not time0 or not time1:
      return
    diff = time1 - time0
    next = time1 + diff
    if selection[-1] != '\n':
      selection += '\n'
    selection += ' ' * indentation + next.strftime(format) + '\n'
    sublime_wrapper.insert(selection, edit, view)
