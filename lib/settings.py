# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Commands to manage settings files. `settings_file` should include a file name
and extension, but not a path. If none is given, use the default Suricate
settings file."""

from contextlib import contextmanager
import os

import sublime

import suricate

from . import sublime_wrapper

suricate.reload_module(sublime_wrapper)


@contextmanager
def load_save_settings(settings_file):
    """Context manager to load and save settings."""
    if not settings_file:
        settings_file = suricate.get_variable('suricate_settings_file_base_name')
    settings = sublime.load_settings(settings_file)
    if not settings:
        message = 'Settings file "%s" not found!' % settings_file
        sublime.error_message(message)
        raise Exception(message)
    # Do not try/catch, don't save if fails.
    yield settings
    sublime.save_settings(settings_file)


def _make_list(obj):
    if obj is None:
        return []
    elif isinstance(obj, (list, tuple, range, set, frozenset)):
        return list(obj)
    elif isinstance(obj, dict):
        return [[key, value] for key, value in obj.items()]
    else:
        return [obj]


def toggle_boolean(key, settings_file=None):
    """Toggle the value of key in settings_file."""
    with load_save_settings(settings_file) as settings:
        value = settings.get(key)
        if isinstance(value, bool):
            settings.set(key, not value)
        else:
            sublime.error_message(
                'Cannot toggle a non-boolean object "%s"' %
                key)


def append_value_to_array(key, value, settings_file=None):
    """Append value to key in settings_file."""
    with load_save_settings(settings_file) as settings:
        lst = settings.get(key, [])
        if isinstance(lst, list):
            lst.append(value)
            settings.set(key, lst)
        else:
            sublime.error_message(
                'Cannot append value to a non-array object "%s"' %
                key)


def set_key_value(key, value, settings_file=None):
    """Set value for key in settings_file."""
    with load_save_settings(settings_file) as settings:
        settings.set(key, value)


def set_from_resources(
        key,
        patterns,
        settings_file=None,
        set_mode='file',
        window=None):
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
    for pattern in _make_list(patterns):
        resources.update(clean(x) for x in sublime.find_resources(pattern))
    on_done = lambda picked: set_key_value(key, picked, settings_file)
    sublime_wrapper.show_quick_panel(sorted(list(resources)), on_done, window)
