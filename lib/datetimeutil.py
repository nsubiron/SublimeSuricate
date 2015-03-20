# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

from datetime import datetime

import sublime

import suricate

from . import sublime_wrapper

suricate.reload_module(sublime_wrapper)


def _datetime_formats():
    defaults = [
        '%Y:%m:%d',
        '%Y/%m/%d',
        '%d/%m/%Y',
        '%d %B %Y',
        '%A, %B %d, %Y',
        '%Y%m%d',
        '%Y%m%d%H%M%S',
        '%a %d',
        '%c',
        'Week %W, day %j',
        '%H:%M:%S',
        '%H:%M',
        '%Y']
    return suricate.get_setting('time_formats', defaults)


def get_times(tstring=None):
    """Return a list of the different formats available for tstring, see
    "time_formats" on settings file. If tstring is None, use current
    time."""
    formats = _datetime_formats()
    if tstring is None:
        time = datetime.now()
    else:
        time, _ = _read_time(tstring, formats)
    if time is None:
        return None
    return [time.strftime(format) for format in formats]


# @todo use dateutil.parser
def _read_time(time_string, time_formats):
    """Try to convert tstring to a format in tformats, return first
    match. If non of them matches, show an error message."""
    for time_format in time_formats:
        try:
            return datetime.strptime(str(time_string), time_format), time_format
        except ValueError:
            pass
    message = 'unknown time format: %r, see %r in settings file.'
    suricate.debuglog(message, time_string, 'time_formats')
    return None, None


def time_to_clipboard(view=None):
    regions = sublime_wrapper.get_selection(view)
    for selection in regions + [None]:
        times = get_times(selection)
        if times is not None:
            break
    sublime_wrapper.show_quick_panel(times, sublime.set_clipboard)


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
    time0, time_format = _read_time(lines[-2].strip(), formats)
    time1, time_format = _read_time(lines[-1].strip(), formats)
    if not time0 or not time1:
        return
    diff = time1 - time0
    incremented = time1 + diff
    if selection[-1] != '\n':
        selection += '\n'
    selection += ' ' * indentation + incremented.strftime(time_format) + '\n'
    sublime_wrapper.insert(selection, edit, view)
