# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import imp
import importlib
import sys

import sublime
import sublime_plugin

DEBUG = False

ForceReloadModules = True

def log(message, *args):
    print('Suricate: ' + message % args)

if DEBUG:
  def debug(message, *args):
      log(message, *args)
else:
  def debug(message, *args):
      pass

def import_module(name, force_reload=ForceReloadModules):
    debug('import %s', name)
    m = importlib.import_module('.' + name, __package__)
    return imp.reload(m) if force_reload else m

class DummyManager(object):
    def update(self, view):
        pass

    def is_enabled(self, key):
        return False

    def run(self, key):
        pass

MANAGER = DummyManager()

def plugin_loaded():
    log('Loading dependencies')
    suricate = import_module('suricate', True)
    suricate.log = log
    suricate.debug = debug
    suricate.import_module = import_module
    sys.modules['suricate'] = suricate
    # Reload suricate package.
    defs = import_module('suricate.defs', True)
    import_module('suricate.flags', True)
    import_module('suricate.util', True)
    import_module('suricate.build_variables', True)
    import_module('suricate.commands', True)
    suricate.Settings = sublime.load_settings(defs.SettingsFileBaseName)
    # Reload plugin package.
    import_module('plugin', True)
    import_module('plugin.menu_manager', True)
    command_manager = import_module('plugin.command_manager', True)
    # Starting up manager.
    global MANAGER
    MANAGER = command_manager.CommandManager()
    MANAGER.load(suricate.Settings)
    suricate.Settings.clear_on_change('Suricate')
    suricate.Settings.add_on_change('Suricate', MANAGER.reload_settings)

class SuricateCommand(sublime_plugin.TextCommand):
    def __init__(self, *args, **kwargs):
        sublime_plugin.TextCommand.__init__(self, *args, **kwargs)
        self._update()

    def _update(self):
        debug('Updating flags for view %s' % self.view.buffer_id())
        self.filename = self.view.file_name()
        self.flags = MANAGER.update(self.filename)

    def is_visible(self, key=None):
        if self.filename != self.view.file_name():
          self._update()
        return MANAGER.is_enabled(key, self.flags)

    def run(self, edit, key):
        args = {'edit': edit, 'view': self.view, 'active_flags': self.flags}
        MANAGER.run(key, args)
