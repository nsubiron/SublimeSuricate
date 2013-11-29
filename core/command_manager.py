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

import imp
import inspect
import sublime

from lib import flags, util

from suricate import *

import menu_manager

def rupdate(lhs, rhs):
    for key, irhs in rhs.items():
      ilhs = lhs.get(key, {})
      ilhs.update(irhs)
      lhs[key] = ilhs

def parse_commands(settings):
    jsoncommands = settings.get('commands', {})
    rupdate(jsoncommands, settings.get('user_commands', {}))
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
    def __init__(self, settings):
        self.flags = 0x0000
        self.view = None
        self.settings = settings
        self.flagmap = {}
        self.commands = {}

    def load(self):
        self.flagmap, self.commands = parse_commands(self.settings)
        menu_manager.print_menus(self.commands)

    def reload_settings(self):
        self.flagmap, self.commands = parse_commands(self.settings)
        menu_manager.print_menus(self.commands, force=True)

    def update(self, view):
        self.view = view
        self.flags = flags.parse(view.file_name())

    def is_enabled(self, key):
        return flags.special_check(self.flags, self.flagmap.get(key, flags.Flags.Never))

    def run(self, key):
        with util.pushd(LibFolder):
          func = self.commands[key][Func]
          args = self.commands[key][Args]
          module_name, function = func.rsplit('.', 1)
          module_info = imp.find_module(module_name, [LibFolder])
          # This do a reload if already imported.
          module = imp.load_module(module_name, *module_info)
          metargs = {'active_flags': int(self.flags), 'view': self.view}
          funcobj = getattr(module, function)
          argspec = inspect.getargspec(funcobj).args
          kwargs = dict((k,i) for k,i in metargs.items() if k in argspec)
          import sublime_wrapper as sw
          kwargs.update(sw.expand_build_variables(args))
          return funcobj(**kwargs)
