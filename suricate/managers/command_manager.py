# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import inspect

import sublime

from .. import commands as command_parser
from .. import flags
from .. import _suricate as suricate

from . import menu_manager


class CommandManager(object):
    def __init__(self):
        self.commands = {}
        self.profiles = []
        self.settings = None

    def load(self, settings):
        self.settings = settings
        self.reload_settings()

    def _clear_on_change(self):
        for profile in self.profiles:
            settings = sublime.load_settings(profile + command_parser.ProfileExtension)
            settings.clear_on_change('CommandManager')

    def _add_on_change(self):
        for profile in self.profiles:
            settings = sublime.load_settings(profile + command_parser.ProfileExtension)
            settings.add_on_change('CommandManager', self.reload_settings)

    def reload_settings(self):
        self._clear_on_change()
        self.profiles = self.settings.get('profiles', [])
        ignore_default_keybindings = self.settings.get('ignore_default_keybindings', False)
        commands = command_parser.get(self.profiles, ignore_default_keybindings)
        # @todo
        folder = suricate.get_variable('suricate_generated_files_path')
        self.commands = menu_manager.print_menus(commands, folder, self.settings)
        self._add_on_change()

    @staticmethod
    def update(filename):
        return flags.parse(filename)

    def is_enabled(self, key, currentflags):
        if key in self.commands:
            return flags.special_check(currentflags, self.commands[key].flags)
        return False

    def run(self, key, metargs):
        call = self.commands[key].call
        args = self.commands[key].args
        module_name, function = call.rsplit('.', 1)
        module = suricate.import_module('lib.' + module_name)
        funcobj = getattr(module, function)
        argspec = inspect.getargspec(funcobj).args
        kwargs = dict((k, i) for k, i in metargs.items() if k in argspec)
        kwargs.update(suricate.expand_variables(args, metargs.get('window')))
        return funcobj(**kwargs)
