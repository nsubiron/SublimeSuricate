# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import sublime

import os

import suricate


def switch_language(view):
    dicts = suricate.get_setting('quick_switch_dictionary_list', [])
    if not dicts:
        dicts = sublime.find_resources('*.dic')
        if not dicts:
            suricate.log('ERROR: no dictionary found')
            return
    current = view.settings().get('dictionary')
    next_item_index = dicts.index(current) + 1 if current in dicts else 0
    next_item = dicts[next_item_index % len(dicts)]
    if next_item in sublime.find_resources('*.dic'):
        view.settings().set('dictionary', next_item)
        sublime.status_message(
            'Dictionary changed to %s' %
            os.path.basename(next_item))
    else:
        sublime.error_message('Dictionary %r not available' % next_item)
