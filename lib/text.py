# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

from suricate import import_module

sublime_wrapper = import_module('lib.sublime_wrapper')

def complete_line(line, char=None, n=80):
    """Returns a string of ``char`` that together with ``line`` sums ``n``
    characters. If ``char`` is ``None`` use ``line``'s last character."""
    if (line or char) and len(line) < n:
      return (line[-1] if char is None else char)*(n-len(line))
    return line

def fill_current_line(edit, view, *args, **kwargs):
    """See text.complete_line.
    @todo It doesn't work as expected, rewrite."""
    getline = lambda region: view.substr(view.line(region.end()))
    func = lambda region: complete_line(getline(region), *args, **kwargs)
    sublime_wrapper.foreach_region(func, edit, view, clear=True)
