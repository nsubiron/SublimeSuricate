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

import json
import os
import sublime

from lib import util

from suricate import *

def print_menus(commands, force=False):
    with util.pushd(SuricateFolder):
      update = force
      manager = MenuManager()
      generated_files = manager.getfilenames()
      if not force:
        mtime = 0
        gettime = lambda filename: os.stat(filename).st_mtime
        for commands_file in util.fwalk('..', CommandsFileBaseName):
          log('File \'%s\', mtime: %s' % (commands_file, gettime(commands_file)))
          mtime = max(mtime, gettime(commands_file))
        outdated = lambda f: not os.path.isfile(f) or gettime(f) < mtime
        if Debug:
          for f in generated_files:
            log('%s, up-to-date: %s' % (f, not outdated(f)))
        update = any(map(outdated, generated_files))
      if update:
        for key in sorted(commands.keys(), key=lambda k: commands[k][Caption]):
          if not manager.add(key, commands[key]):
            del commands[key]
        manager.writeout()
        sublime.status_message('Suricate commands and menus updated.')

class SublimeFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.base = []
        self.groups = {}

    def add(self, data, group=None):
        if group is None:
          self.base.append(data)
        else:
          if group not in self.groups:
            self.groups[group] = []
          self.groups[group].append(data)

    def asdata(self):
        data = self.base
        for key in sorted(self.groups.keys()):
          sub = self.groups[key]
          if sub:
            data.append({'caption': '-'})
            data += sub
        return data

    def writeout(self):
        with open(self.filename, 'w+') as f:
          f.write(json.dumps(self.asdata(), indent=2))

class MenuManager(object):
    def __init__(self):
        self.smain = SublimeFile(None)
        self.pmain = SublimeFile(None)
        self.commands = SublimeFile('Suricate.sublime-commands')
        self.main = SublimeFile('Main.sublime-menu')
        self.context = SublimeFile('Context.sublime-menu')
        platform = sublime.platform().title()
        self.keymap = SublimeFile('Default (%s).sublime-keymap' % platform)

    def getfilenames(self):
        files = [self.commands, self.main, self.context, self.keymap]
        return map(lambda sf: sf.filename, files)

    def add(self, key, command):
        group = command[Group] if command[Group] is not None else ''
        if group.endswith('.dev'):
          if not GlobalSettings.get('dev_mode', False):
            return False
          group = group[:-4]
        log('Adding command \'%s\': %s' % (key, command))
        sublimecmd = command[Func].startswith('sublime.')
        if sublimecmd:
          _, cmd = command[Func].rsplit('.', 1)
          basic = {'command': cmd, 'args': command[Args]}
        else:
          basic = {'command': 'suricate', 'args': {'key': key}}
        if not group.startswith('.'):
          caption = command[Caption]
          quickpanel = dict(basic)
          quickpanel['caption'] = 'Suricate: %s' % caption
          menus = dict(basic)
          menus['caption'] = caption
          if command[Mnemonic]:
            menus['mnemonic'] = command[Mnemonic]
          self.commands.add(quickpanel)
          if command[Context]:
            self.context.add(menus, group)
          if group is not None and group.startswith('main.'):
            if group.startswith('main.preferences'):
              self.pmain.add(menus, group)
            else:
              self.smain.add(menus, group)
        if command[Keys]:
          keybinding = dict(basic)
          keybinding['keys'] = command[Keys]
          self.keymap.add(keybinding)
        return not sublimecmd

    def writeout(self):
        self.commands.writeout()
        self.context.writeout()
        self.keymap.writeout()
        self._fill_main_menu()
        self.main.writeout()

    def _fill_main_menu(self):
        suricate_settings = {"caption": "Suricate", "children": self.pmain.asdata()}
        package_settings = {"id": "package-settings", "children": [suricate_settings]}
        preferences_menu = {"id": "preferences", "children": [package_settings]}
        self.main.add(preferences_menu)
        if GlobalSettings.get('dev_mode', False) and \
           GlobalSettings.get("show_suricate_menu", False):
          suricate_menu = {
              'caption': 'Suricate',
              'mnemonic': 'u',
              'id': 'Suricate',
              'children': self.smain.asdata()}
          self.main.add(suricate_menu)
