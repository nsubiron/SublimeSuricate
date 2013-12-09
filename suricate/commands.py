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

from collections import namedtuple

from . import defs
from . import flags
from . import util

ProfileExtension = '.suricate-commands'

DefaultDefaults = {'group': None, 'args': {}, 'flags': None, 'keys': [], 'context': False}

TagList = ["caption", "mnemonic", "group", "func", "args", "flags", "keys", "context"]

Command = namedtuple('Command', TagList)

def _rupdate(lhs, rhs):
    for key, irhs in rhs.items():
      ilhs = lhs.get(key, {})
      ilhs.update(irhs)
      lhs[key] = ilhs

def _create_commands(settings):
    commands = {}
    jsoncommands = settings.get('commands', {})
    _rupdate(jsoncommands, settings.get('user_commands', {}))
    defaults = jsoncommands.pop('defaults', DefaultDefaults)
    for key, item in jsoncommands.items():
      try:
        args = dict(defaults)
        args.update(item)
        args['flags'] = flags.from_string(str(args['flags']))
        command = Command(**args)
        if flags.check_platform(command.flags):
          commands[key] = command
      except TypeError as e:
        print('Command "%s" not added: mandatory field missing.' % key)
    return commands

def get(profiles):
    commands = {}
    for profile in profiles:
      settings = sublime.load_settings(profile + ProfileExtension)
      commands.update(_create_commands(settings))
    return commands


