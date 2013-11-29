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

import os
import sublime
import sublime_plugin

# Global definitions

CommandsFileBaseName = 'SuricateCommands.json'
SettingsFileBaseName = 'Suricate.sublime-settings'
SuricateFolder = os.path.dirname(os.path.abspath(__file__))
LibName = 'lib'
LibFolder = os.path.join(SuricateFolder, LibName)

GlobalSettings = sublime.load_settings(SettingsFileBaseName)

DefaultDefaults = {'group': None, 'args': {}, 'flags': None, 'keys': [], 'context': False}

TagList = ["caption", "mnemonic", "group", "func", "args", "flags", "keys", "context"]

Caption  = 0
Mnemonic = 1
Group    = 2
Func     = 3
Args     = 4
Flags    = 5
Keys     = 6
Context  = 7

Debug = GlobalSettings.get('debug', False)

if Debug:
  def log(x): print(x)
else:
  def log(x): pass

# Import core library.

from core.command_manager import CommandManager

def init():
    settings = sublime.load_settings(CommandsFileBaseName)
    manager = CommandManager(settings)
    settings.clear_on_change('Suricate')
    settings.add_on_change('Suricate', manager.reload_settings)
    GlobalSettings.add_on_change('Suricate', manager.reload_settings)
    return manager

Manager = init()

# This updates sublime menus and commands if needed (time in millisecons).
sublime.set_timeout(Manager.load, 2000)

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
