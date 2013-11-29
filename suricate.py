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

import sublime
import sublime_plugin

# Import core library.
try:
  # Python 3
  from .core import defs
  from .core.command_manager import CommandManager
except ValueError:
  # Python 2
  from core import defs
  from core.command_manager import CommandManager

# Put definitions at global scope so modules in lib can use them.
import sys
sys.modules['suricate'] = defs

Manager = CommandManager()

def plugin_loaded():
    settings = sublime.load_settings(defs.CommandsFileBaseName)
    Manager.load(settings)
    settings.clear_on_change('Suricate')
    settings.add_on_change('Suricate', Manager.reload_settings)
    defs.GlobalSettings.add_on_change('Suricate', Manager.reload_settings)

if int(sublime.version()) < 3000:
  sublime.set_timeout(plugin_loaded, 2000)

class FileEventListener(sublime_plugin.EventListener):
    def on_post_save(self, view):
        Manager.update(view)

    def on_activated(self, view):
        Manager.update(view)

class SuricateCommand(sublime_plugin.ApplicationCommand):
    def is_visible(self, key):
        return Manager.is_enabled(key)

    def run(self, key):
        Manager.run(key)
