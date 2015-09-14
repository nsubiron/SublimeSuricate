# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import json
import os

import sublime

from .. import _suricate as suricate


def _get_menu_variables():
    variables = suricate.extract_variables()
    def _get_key_value(key, value):
        if key.startswith('suricate_'):
            return (key, value)
        return (key, '${%s}' % key)
    return dict(_get_key_value(*x) for x in variables.items())


def print_menus(commands, folder, settings):
    """Generate sublime files based on commands. Return the commands dictionary
    filtering out the commands not added."""
    if not os.path.exists(folder):
        os.mkdir(folder)
    manager = _MenuManager(folder, settings)
    for key in sorted(commands.keys(), key=lambda k: commands[k].caption):
        if not manager.add(key, commands[key]):
            del commands[key]
    manager.write_out()
    sublime.status_message('Suricate commands and menus updated.')
    return commands


class _SublimeData(object):

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

    def as_data(self):
        data = self.base
        for i, key in enumerate(sorted(self.groups.keys())):
            sub = self.groups[key]
            if sub:
                if i > 0:
                    data.append({'caption': '-'})
                data += sub
        return data


class _SublimeFile(_SublimeData):

    def __init__(self, path, basename):
        super().__init__()
        self.filename = os.path.join(path, basename)

    def write_out(self, variables):
        with open(self.filename, 'w+') as fd:
            data = suricate.expand_variables(self.as_data(), variables)
            fd.write(json.dumps(data, indent='\t'))


# @todo remove
import fnmatch
import re
def _regex_callable(patterns):
    if patterns is None:
        return lambda x: False
    if isinstance(patterns, str):
        patterns = [patterns]
    regex = re.compile(r'|'.join(fnmatch.translate(p) for p in patterns))
    return lambda x: regex.match(x) is not None


class _MenuManager(object):

    def __init__(self, folder, settings):
        self.smain = _SublimeData()
        self.pmain = _SublimeData()
        self.scontext = _SublimeData()
        self.commands = _SublimeFile(folder, 'Suricate.sublime-commands')
        self.main = _SublimeFile(folder, 'Main.sublime-menu')
        self.context = _SublimeFile(folder, 'Context.sublime-menu')
        self.keymap = _SublimeFile(folder, 'Default.sublime-keymap')
        # Settings.
        self.dev_mode = settings.get('dev_mode', False)
        self.override_ctrl_o = settings.get('override_ctrl_o', False)
        self.show_suricate_menu = settings.get('show_suricate_menu', False)
        self.show_context_menu = settings.get('add_entries_to_context_menu', True)
        self.nest_context_items = settings.get('single_context_menu_entry', False)
        ignore_list = settings.get('ignore_groups', [])
        if not ignore_list:
            ignore_list = None
        self.ignore_groups = _regex_callable(ignore_list)

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
            if self.show_context_menu and command.context_menu:
                self.scontext.add(menus, group)
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

    def write_out(self):
        variables = _get_menu_variables()
        self._fill_main_menu()
        self._fill_context_menu()
        self.commands.write_out(variables)
        self.context.write_out(variables)
        self.keymap.write_out(variables)
        self.main.write_out(variables)

    def _group_is_valid(self, group):
        if group.endswith('.dev') and not self.dev_mode:
            return False
        return not self.ignore_groups(group)

    def _override_keys(self, keys):
        if self.override_ctrl_o and keys[0].lower() == 'ctrl+o':
            keys = [self.override_ctrl_o] + keys[1:]
        return keys

    def _fill_main_menu(self):
        suricate_settings = {
            "caption": "Suricate",
            "children": self.pmain.as_data()}
        package_settings = {
            "id": "package-settings",
            "children": [suricate_settings]}
        preferences_menu = {
            "id": "preferences",
            "children": [package_settings]}
        self.main.add(preferences_menu)
        if self.dev_mode and self.show_suricate_menu:
            suricate_menu = {
                'caption': 'Suricate',
                'mnemonic': 'u',
                'id': 'suricate',
                'children': self.smain.as_data()}
            self.main.add(suricate_menu)

    def _fill_context_menu(self):
        if not self.show_context_menu:
            return
        if self.nest_context_items:
            suricate_items = {
                'caption': 'Suricate',
                'mnemonic': 'u',
                'id': 'suricate',
                'children': self.scontext.as_data()}
            self.context.add(suricate_items)
        else:
            for item in self.scontext.as_data():
                self.context.add(item)

