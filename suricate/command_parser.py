# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import collections

import sublime

from . import _suricate as suricate
from . import flags


_DEFAULT_DEFAULTS = \
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


_TAG_LIST = ['call'] + [x for x in _DEFAULT_DEFAULTS.keys()]


Command = collections.namedtuple('Command', _TAG_LIST)


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
    defaults = profile.get('defaults', _DEFAULT_DEFAULTS)
    for key, item in jsoncommands.items():
        try:
            args = dict(defaults)
            args.update(item)
            args['flags'] = flags.from_string(str(args['flags']))
            command = Command(**args)
            if flags.check_platform(command.flags):
                commands[key] = command
        except TypeError as exception:
            suricate.debuglog('Exception %s', exception)
            suricate.log(
                'WARNING: Command %r not added: mandatory field missing.',
                key)
    return commands


def parse_profiles(profiles, ignore_default_keybindings):
    commands = {}
    for profile_file_name in profiles:
        profile = sublime.load_settings(profile_file_name)
        commands.update(_create_commands(profile, ignore_default_keybindings))
    return commands
