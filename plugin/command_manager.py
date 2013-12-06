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

import inspect

import sublime

from suricate import build_variables
from suricate import commands as command_parser
from suricate import defs
from suricate import flags
from suricate import import_module

from . import menu_manager

class CommandManager(object):
    def __init__(self):
        self.commands = {}
        self.profiles = []

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
        commands = command_parser.get(self.profiles)
        self.commands = menu_manager.print_menus(commands, defs.SuricatePath, self.settings)
        self._add_on_change()

    def update(self, filename):
        return flags.parse(filename)

    def is_enabled(self, key, currentflags):
        if key in self.commands:
          return flags.special_check(currentflags, self.commands[key].flags)
        return False

    def run(self, key, metargs):
        func = self.commands[key].func
        args = self.commands[key].args
        module_name, function = func.rsplit('.', 1)
        module = import_module('lib.' + module_name)
        funcobj = getattr(module, function)
        argspec = inspect.getargspec(funcobj).args
        kwargs = dict((k,i) for k,i in metargs.items() if k in argspec)
        kwargs.update(build_variables.expand(args))
        return funcobj(**kwargs)
