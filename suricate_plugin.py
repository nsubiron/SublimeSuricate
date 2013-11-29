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

import imp
import os
import sys

import sublime
import sublime_plugin

Verbose = True

SuricateFolder = os.path.dirname(os.path.abspath(__file__))

try:

  import importlib

  def reload_module(modulename):
      if Verbose: print('-- reloading ' + modulename)
      m = importlib.import_module('.' + modulename, __package__)
      return imp.reload(m)

except ImportError:

  def reload_module(modulename):
      if Verbose: print('-- reloading ' + modulename)
      root, modulename = modulename.rsplit('.', 1)
      path = os.path.abspath(os.path.join(SuricateFolder, root.replace('.', os.sep)))
      fp, pathname, description = imp.find_module(modulename, [path])
      try:
        # This do a reload if already imported.
        return imp.load_module(modulename, fp, pathname, description)
      finally:
        if fp:
          fp.close()

class DummyManager(object):
    def update(self, view):
        pass

    def is_enabled(self, key):
        return False

    def run(self, key):
        pass

class ManagerHolder(object):
    def __init__(self, manager):
        self.manager = manager

    def set(self, manager):
        self.manager = manager

Holder = ManagerHolder(DummyManager())

def plugin_loaded():
    print('reloading %s dependencies' % __name__)
    # Reload suricate package.
    reload_module('suricate.pybase')
    defs = reload_module('suricate.defs')
    reload_module('suricate.flags')
    reload_module('suricate.util')
    reload_module('suricate.build_variables')
    suricate = reload_module('suricate')
    suricate.reload_module = reload_module
    suricate.Settings = sublime.load_settings(defs.SettingsFileBaseName)
    sys.modules['suricate'] = suricate
    # Reload plugin package.
    reload_module('plugin.menu_manager')
    command_manager = reload_module('plugin.command_manager')
    commands = sublime.load_settings(defs.CommandsFileBaseName)
    # Starting up manager.
    manager = command_manager.CommandManager()
    manager.load(commands, suricate.Settings)
    commands.clear_on_change('Suricate')
    commands.add_on_change('Suricate', manager.reload_settings)
    suricate.Settings.clear_on_change('Suricate')
    suricate.Settings.add_on_change('Suricate', manager.reload_settings)
    Holder.set(manager)

if sublime.version() < '3000':
  sublime.set_timeout(plugin_loaded, 2000)

class SuricateCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        sublime_plugin.TextCommand.__init__(self, *args, **kwargs)
        self._update()

    def _update(self):
        if Verbose: print('Updating flags for view %s' % self.view.buffer_id())
        self.filename = self.view.file_name()
        self.flags = Holder.manager.update(self.filename)

    def is_visible(self, key):
        if self.filename != self.view.file_name():
          self._update()
        return Holder.manager.is_enabled(key, self.flags)

    def run(self, edit, key):
        args = {'edit': edit, 'view': self.view, 'active_flags': self.flags}
        Holder.manager.run(key, args)
