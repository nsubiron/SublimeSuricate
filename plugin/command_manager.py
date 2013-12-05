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
import sys

from suricate import build_variables
from suricate import flags
from suricate import import_module
from suricate import util

from suricate.defs import *

from .menu_manager import print_menus

def rupdate(lhs, rhs):
    for key, irhs in rhs.items():
      ilhs = lhs.get(key, {})
      ilhs.update(irhs)
      lhs[key] = ilhs

def parse_commands(command_settings):
    jsoncommands = command_settings.get('commands', {})
    rupdate(jsoncommands, command_settings.get('user_commands', {}))
    defaults = jsoncommands.pop('defaults', DefaultDefaults)
    retrieve = lambda item, tag: item[tag] if tag in item else defaults[tag]
    commands = {}
    flagmap = {}
    for key, item in jsoncommands.items():
      try:
        list_format = [retrieve(item, tag) for tag in TagList]
        commandflags = flags.from_string(str(list_format[Flags]))
        if flags.check_platform(commandflags):
          flagmap[key] = commandflags
          commands[key] = list_format
      except KeyError:
        pass
    return flagmap, commands

class CommandManager(object):
    def __init__(self):
        self.flagmap = {}
        self.commands = {}

    def load(self, command_settings, settings):
        self.command_settings = command_settings
        self.settings = settings
        self.flagmap, self.commands = parse_commands(self.command_settings)
        print_menus(self.commands, self.settings, force=False)

    def reload_settings(self):
        self.flagmap, self.commands = parse_commands(self.command_settings)
        print_menus(self.commands, self.settings, force=True)

    def update(self, filename):
        return flags.parse(filename)

    def is_enabled(self, key, currentflags):
        return flags.special_check(currentflags, self.flagmap.get(key, flags.Flags.Never))

    def run(self, key, metargs):
        func = self.commands[key][Func]
        args = self.commands[key][Args]
        module_name, function = func.rsplit('.', 1)
        module = import_module('lib.' + module_name)
        funcobj = getattr(module, function)
        argspec = inspect.getargspec(funcobj).args
        kwargs = dict((k,i) for k,i in metargs.items() if k in argspec)
        kwargs.update(build_variables.expand(args))
        with util.pushd(LibFolder):
          return funcobj(**kwargs)
