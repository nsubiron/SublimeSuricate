# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import sublime

import suricate

from collections import namedtuple

from . import flags

ProfileExtension = '.suricate-profile'

DefaultDefaults = \
    {
        'caption':        'No description provided',
        'mnemonic':       None,
        'group':          None,
        'args':           {},
        'flags':          None,
        'keys':           [],
        'context':        None,
        'context_menu':   False
    }

TagList = \
    [
        'caption',
        'mnemonic',
        'group',
        'call',
        'args',
        'flags',
        'keys',
        'context',
        'context_menu'
    ]

Command = namedtuple('Command', TagList)

def _rupdate(lhs, rhs):
    for key, irhs in rhs.items():
      ilhs = lhs.get(key, {})
      ilhs.update(irhs)
      lhs[key] = ilhs

def _remove_key_bindings(jsoncommands):
    for item in jsoncommands.values():
      if 'keys' in item:
        item.pop('keys')

def _create_commands(profile, ignore_default_keybindings):
    commands = {}
    jsoncommands = profile.get('commands', {})
    if ignore_default_keybindings:
      _remove_key_bindings(jsoncommands)
    _rupdate(jsoncommands, profile.get('user_commands', {}))
    defaults = profile.get('defaults', DefaultDefaults)
    for key, item in jsoncommands.items():
      try:
        args = dict(defaults)
        args.update(item)
        args['flags'] = flags.from_string(str(args['flags']))
        command = Command(**args)
        if flags.check_platform(command.flags):
          commands[key] = command
      except TypeError as exception:
        suricate.debug('Exception %s', exception)
        suricate.log('WARNING: Command "%s" not added: mandatory field missing.', key)
    return commands

def get(profiles, ignore_default_keybindings):
    commands = {}
    for profile_name in profiles:
      profile = sublime.load_settings(profile_name + ProfileExtension)
      commands.update(_create_commands(profile, ignore_default_keybindings))
    return commands
