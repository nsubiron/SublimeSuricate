# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

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


