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
        'selector':       None,
        'context':        None,
        'context_menu':   False
    }


_TAG_LIST = ['call'] + [x for x in _DEFAULT_DEFAULTS.keys()]


_PLATFORM_EXTENSION = '.' + sublime.platform()


Command = collections.namedtuple('Command', _TAG_LIST)


def _rupdate(lhs, rhs):
    for key, irhs in rhs.items():
        ilhs = lhs.get(key, {})
        ilhs.update(irhs)
        lhs[key] = ilhs


def _remove_key_bindings(data):
    for item in data.values():
        for key in ['keys', 'keys' + _PLATFORM_EXTENSION]:
            if key in item:
                item.pop(key)


def _merge_platform_specific_tags(raw_data):
    data = {}
    for tag in _TAG_LIST:
        os_tag = tag + _PLATFORM_EXTENSION
        if os_tag in raw_data:
            data[tag] = raw_data[os_tag]
        elif tag in raw_data:
            data[tag] = raw_data[tag]
    return data


def _get_commands(profile, key):
    data = profile.get(key, {})
    return dict((k, _merge_platform_specific_tags(v)) for k, v in data.items())


def _create_commands(profile, ignore_default_keybindings):
    commands = {}
    data = _get_commands(profile, 'commands')
    if ignore_default_keybindings:
        _remove_key_bindings(data)
    user_data = _get_commands(profile, 'user_commands')
    _rupdate(data, user_data)
    defaults = _merge_platform_specific_tags(profile.get('defaults', _DEFAULT_DEFAULTS))
    for key, item in data.items():
        try:
            args = dict(defaults)
            args.update(item)
            args['flags'] = flags.from_string(str(args['flags']))
            if flags.check_platform(args['flags']):
                commands[key] = Command(**args)
        except Exception as exception:
            suricate.log('WARNING: Command %r not added: %s', key, exception)
    return commands


def parse_profiles(profiles, ignore_default_keybindings):
    commands = {}
    for profile_file_name in profiles:
        profile = sublime.load_settings(profile_file_name)
        commands.update(_create_commands(profile, ignore_default_keybindings))
    return commands
