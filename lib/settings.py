# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import os
import sublime

from suricate import defs
from suricate import import_module
from suricate import util

sublime_wrapper = import_module('lib.sublime_wrapper')

def toggle_boolean(key, base_name=defs.SettingsFileBaseName):
    settings = sublime.load_settings(base_name)
    value = settings.get(key)
    if isinstance(value, bool):
      settings.set(key, not value)
      sublime.save_settings(base_name)
    else:
      sublime.error_message('Cannot toggle a non-boolean object "%s"' % key)

def set_key_value(key, value, filename):
    """Set value for key in settings filename, filename should include a file
    name and extension, but not a path."""
    settings = sublime.load_settings(filename)
    if not settings:
      sublime.error_message('Settings "%s" not found!' % filename)
    else:
      settings.set(key, value)
      sublime.save_settings(filename)

def set_from_resources(key, patterns, settings_file, set_mode='file', window=None):
    """Set the key in settings_file from a list of resources found based on
    patterns. Available values for `set_mode`:
      * "file": `Packages/Default/Preferences.sublime-settings`
      * "file_name": `Preferences.sublime-settings`
      * "file_base_name": `Preferences`
    """
    resources = set()
    if set_mode == 'file':
      clean = lambda x: x
    elif set_mode == 'file_name':
      clean = os.path.basename
    elif set_mode == 'file_base_name':
      clean = lambda x: os.path.splitext(os.path.basename(x))[0]
    else:
      sublime.error_message('Unknown set_mode "%s".' % set_mode)
      return
    for pattern in util.make_list(patterns):
      resources.update(clean(x) for x in sublime.find_resources(pattern))
    on_done = lambda picked: set_key_value(key, picked, settings_file)
    sublime_wrapper.show_quick_panel(sorted(list(resources)), on_done, window)
