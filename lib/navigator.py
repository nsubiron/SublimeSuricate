# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import os
import sublime

from suricate import Settings
from suricate import build_variables
from suricate import import_module
from suricate import util

process = import_module('lib.process')
sublime_wrapper = import_module('lib.sublime_wrapper')

OpenMode = 'open'
LaunchMode = 'launch'

def exclude_patterns(exclude_binaries):
    """Return a pair of callable objects that matches any exclude pattern in
    global settings, for folders and files respectively."""
    settings = sublime.load_settings('Global.sublime-settings')
    folder_exclude = settings.get('folder_exclude_patterns')
    file_exclude = settings.get('file_exclude_patterns')
    if exclude_binaries:
      file_exclude += settings.get('binary_file_patterns')
    return util.regex_callable(folder_exclude), util.regex_callable(file_exclude)

def launch(mode=OpenMode, view=None):
    """Open navigator quick panel.
      * ``mode=='open'`` Open selected file with Sublime Text
      * ``mode=='launch'`` Try to externally launch selected file"""
    if mode != OpenMode and mode != LaunchMode:
      raise Exception('Unknown mode!')
    window = sublime.active_window()
    settingskey = 'quick_%s_path_list' % mode
    paths = build_variables.expand(Settings.get(settingskey))
    factory = _ItemFactory(mode, window)
    items = []
    if view is not None:
      current_file = view.file_name()
      if current_file is not None:
        if mode == LaunchMode:
          items.append(factory.create(current_file, 'Current file'))
        items.append(factory.create(os.path.dirname(current_file), 'Current folder'))
    pathitems = [factory.create(path, os.path.basename(path)) for path in paths]
    items += sorted(x for x in pathitems if x is not None)
    _show_quick_panel(items)

def _show_quick_panel(items):
    if items and isinstance(items, list):
      items = [x for x in items if x is not None]
      on_done = lambda picked: _show_quick_panel(picked.on_done())
      sublime_wrapper.show_quick_panel(items, on_done)

class _ListItem(list):
    def __init__(self, label, info, path, on_done):
        self.on_done = lambda: on_done(path)
        list.__init__(self, [label, info + path])

class _ItemFactory(object):
    def __init__(self, mode, window):
        self.mode = mode
        self.direxcl, self.filexcl = exclude_patterns(mode == OpenMode)
        if mode == OpenMode:
          self.on_done_file = window.open_file
        else:
          self.on_done_file = process.start_file

    def from_folder(self, path):
        parent = self.create(os.path.join(path, '..'), '..')
        try:
          items = [self.create(os.path.join(path, name), name) for name in os.listdir(path)]
          return [parent] + items
        except OSError as e:
          return [parent, self.create(path, e.strerror)]

    def create(self, path, label):
        path = os.path.abspath(path)
        if os.path.isdir(path) and not self.direxcl(os.path.basename(path)):
          if label == '':
            label = path
          return _ListItem(label, 'Open folder; ', path, self.from_folder)
        elif os.path.isfile(path) and not self.filexcl(os.path.basename(path)):
          return _ListItem(label, '%s file; ' % self.mode.title(), path, self.on_done_file)
        return None
