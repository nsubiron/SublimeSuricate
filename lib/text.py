# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import random

import suricate

from . import sublime_wrapper

suricate.reload_module(sublime_wrapper)


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


def line_length(line, tab_width):
    return len(line) + line.count('\t') * (tab_width - 1)


def complete_line(line, max_line_length, tab_width, char=None):
    """Returns a string of `char` that together with `line` sums
    `max_line_length` characters. If `char` is `None` use `line`'s last
    character."""
    length = line_length(line, tab_width)
    if (line or char) and length < max_line_length:
        return (line[-1] if char is None else char) * \
            (max_line_length - length)
    return line


def split_line(line, max_line_length):
    """@todo Only splits on spaces."""
    index = line.rfind(' ', 0, max_line_length + 1)
    if index == -1:
        return line
    leading_spaces = len(line) - len(line.lstrip())
    return line[:index] + '\n' + leading_spaces * ' ' + line[index + 1:]


def fill_current_line(edit, view, max_line_length=None, char=None):
    """@todo It doesn't work as expected, rewrite."""
    max_line_length = get_max_line_length(view, max_line_length)
    tab_size = view.settings().get('tab_size', 4)
    getline = lambda region: view.substr(view.line(region.end()))
    func = lambda region: complete_line(
        getline(region),
        max_line_length,
        tab_size,
        char)
    sublime_wrapper.foreach_region(func, edit, view, clear=True)


def split_current_line(edit, view, max_line_length=None):
    max_line_length = get_max_line_length(view, max_line_length)
    for region in view.sel():
        line = view.line(region.end())
        if line.size() > max_line_length:
            view.replace(
                edit,
                line,
                split_line(
                    view.substr(line),
                    max_line_length))


def randomize(edit, view):
    alphabet = "_{}[]#()<>%$:;.?*+-\\/^&|~!=,'0123456789" \
               "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for region in view.sel():
        if region.size() > 0:
            chars = [random.choice(alphabet) for x in range(0, region.size())]
            view.replace(edit, region, ''.join(chars))
        else:
            view.insert(edit, region.end(), random.choice(alphabet))
