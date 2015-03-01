# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import inspect

import sublime

from .. import _suricate as suricate
from .. import command_parser
from .. import flags

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
            settings = sublime.load_settings(profile)
            settings.clear_on_change('SuricateCommandManager')

    def _add_on_change(self):
        for profile in self.profiles:
            settings = sublime.load_settings(profile)
            settings.add_on_change(
                'SuricateCommandManager',
                self.reload_settings)

    def reload_settings(self):
        self._clear_on_change()
        profile_extension = suricate.get_variable('suricate_profile_extension')
        active_profiles = self.settings.get('profiles', [])
        self.profiles = [x + profile_extension for x in active_profiles if x]
        commands = command_parser.parse_profiles(
            self.profiles,
            self.settings.get('ignore_default_keybindings', False))
        # @todo
        folder = suricate.get_variable('suricate_generated_files_path')
        self.commands = menu_manager.print_menus(
            commands,
            folder,
            self.settings)
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
        module = suricate.import_module(module_name)
        funcobj = getattr(module, function)
        argspec = inspect.getargspec(funcobj).args
        kwargs = dict((k, i) for k, i in metargs.items() if k in argspec)
        kwargs.update(
            suricate.expand_variables(
                args,
                window=metargs.get('window')))
        return funcobj(**kwargs)
