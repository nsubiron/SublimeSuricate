# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

from suricate import import_module

sublime_wrapper = import_module('lib.sublime_wrapper')

def get_max_line_length(view, guess):
    if guess:
      try:
        return int(guess)
      except TypeError:
        pass
    if view.settings().get("wrap_width"):
      try:
        return int(view.settings().get("wrap_width"))
      except TypeError:
        pass
    if view.settings().get("rulers"):
      try:
        return int(view.settings().get("rulers")[0])
      except ValueError:
        pass
      except TypeError:
        pass
    return 78

def complete_line(line, max_line_length, char=None):
    """Returns a string of `char` that together with `line` sums
    `max_line_length` characters. If `char` is `None` use `line`'s last
    character."""
    if (line or char) and len(line) < max_line_length:
      return (line[-1] if char is None else char)*(max_line_length-len(line))
    return line

def split_line(line, max_line_length):
    """@todo Only splits on spaces."""
    index = line.rfind(' ', 0, max_line_length + 1)
    leading_spaces = len(line) - len(line.lstrip())
    return line[:index] + '\n' + leading_spaces * ' ' + line[index + 1:]

def fill_current_line(edit, view, max_line_length=None, char=None):
    """@todo It doesn't work as expected, rewrite."""
    max_line_length = get_max_line_length(view, max_line_length)
    getline = lambda region: view.substr(view.line(region.end()))
    func = lambda region: complete_line(getline(region), max_line_length, char)
    sublime_wrapper.foreach_region(func, edit, view, clear=True)

def split_current_line(edit, view, max_line_length=None):
    max_line_length = get_max_line_length(view, max_line_length)
    for region in view.sel():
      line = view.line(region.end())
      if line.size() > max_line_length:
        view.replace(edit, line, split_line(view.substr(line), max_line_length))
