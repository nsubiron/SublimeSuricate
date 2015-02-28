# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import json
import os
import sublime

from .. import util
from .._suricate import _SuricateAPI as SuricateAPI

CommandsFileBaseName =    'Suricate.sublime-commands'
MainMenuFileBaseName =    'Main.sublime-menu'
ContextMenuFileBaseName = 'Context.sublime-menu'
KeymapFileBaseName =      'Default (%s).sublime-keymap' % sublime.platform().title()


def get_menu_variables():
    SuricateBaseName = SuricateAPI.package_name
    SuricateMenuVariables = {
      'suricate_base_name': SuricateBaseName,
      'suricate_package_path': '${packages}/' + SuricateBaseName,
      'suricate_path': '${packages}/' + SuricateBaseName
    }
    return SuricateMenuVariables

def print_menus(commands, folder, settings):
    """Generate sublime files based on commands. Return the commands dictionary
    filtering out the commands not added."""
    print(folder)
    if not os.path.exists(folder):
      os.mkdir(folder)
    manager = MenuManager(folder, settings)
    for key in sorted(commands.keys(), key=lambda k: commands[k].caption):
      if not manager.add(key, commands[key]):
        del commands[key]
    manager.writeout()
    sublime.status_message('Suricate commands and menus updated.')
    return commands

class SublimeData(object):
    def __init__(self):
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

class SublimeFile(SublimeData):
    def __init__(self, path, basename):
        SublimeData.__init__(self)
        self.filename = os.path.join(path, basename)

    def writeout(self):
        with open(self.filename, 'w+') as f:
          data = util.replacekeys(self.asdata(), get_menu_variables())
          f.write(json.dumps(data, indent='\t'))

class MenuManager(object):
    def __init__(self, folder, settings):
        self.smain = SublimeData()
        self.pmain = SublimeData()
        self.commands = SublimeFile(folder, CommandsFileBaseName)
        self.main = SublimeFile(folder, MainMenuFileBaseName)
        self.context = SublimeFile(folder, ContextMenuFileBaseName)
        self.keymap = SublimeFile(folder, KeymapFileBaseName)
        # Settings.
        self.dev_mode = settings.get('dev_mode', False)
        self.override_ctrl_o = settings.get('override_ctrl_o', False)
        self.show_suricate_menu = settings.get('show_suricate_menu', False)
        ignore_list = settings.get('ignore_groups', [])
        if not ignore_list:
          ignore_list = None
        self.ignore_groups = util.regex_callable(ignore_list)

    def getfilenames(self):
        files = [self.commands, self.main, self.context, self.keymap]
        return [x.filename for x in files]

    def add(self, key, command):
        group = command.group if command.group is not None else ''
        if not self._group_is_valid(group):
          return False
        if group.endswith('.dev'):
          group = group[:-4]
        sublimecmd = command.call.startswith('sublime.')
        if sublimecmd:
          _, cmd = command.call.rsplit('.', 1)
          basic = {'command': cmd, 'args': command.args}
        else:
          basic = {'command': 'suricate', 'args': {'key': key}}
        if not group.startswith('.'):
          caption = command.caption
          quickpanel = dict(basic)
          quickpanel['caption'] = 'Suricate: %s' % caption
          menus = dict(basic)
          menus['caption'] = caption
          if command.mnemonic:
            menus['mnemonic'] = command.mnemonic
          self.commands.add(quickpanel)
          if command.context_menu:
            self.context.add(menus, group)
          if group is not None and group.startswith('main.'):
            if group.startswith('main.preferences'):
              self.pmain.add(menus, group)
            else:
              self.smain.add(menus, group)
        if command.keys:
          keybinding = dict(basic)
          keybinding['keys'] = self._override_keys(command.keys)
          if command.context:
            keybinding['context'] = command.context
          self.keymap.add(keybinding)
        return not sublimecmd

    def writeout(self):
        self.commands.writeout()
        self.context.writeout()
        self.keymap.writeout()
        self._fill_main_menu()
        self.main.writeout()

    def _group_is_valid(self, group):
        if group.endswith('.dev') and not self.dev_mode:
          return False
        return not self.ignore_groups(group)

    def _override_keys(self, keys):
        if self.override_ctrl_o and keys[0].lower() == 'ctrl+o':
          keys = [self.override_ctrl_o] + keys[1:]
        return keys

    def _fill_main_menu(self):
        suricate_settings = {"caption": "Suricate", "children": self.pmain.asdata()}
        package_settings = {"id": "package-settings", "children": [suricate_settings]}
        preferences_menu = {"id": "preferences", "children": [package_settings]}
        self.main.add(preferences_menu)
        if self.dev_mode and self.show_suricate_menu:
          suricate_menu = {
              'caption': 'Suricate',
              'mnemonic': 'u',
              'id': 'Suricate',
              'children': self.smain.asdata()}
          self.main.add(suricate_menu)
