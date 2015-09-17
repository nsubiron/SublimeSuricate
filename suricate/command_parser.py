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


_PLATFORM = sublime.platform()


Command = collections.namedtuple('Command', _TAG_LIST)


class _CommandParser(object):
    def __init__(self, settings):
        self.ignore_default_keybindings = settings.get('ignore_default_keybindings', False)
        self.override_ctrl_o = settings.get('override_default_opening_key', False)
        key_map = settings.get('key_map', {})
        self.os_key_map = dict(key_map.get('*', {}))
        self.os_key_map.update(dict(key_map.get(_PLATFORM, {})))
        self.commands = {}

    def parse(self, profile):
        data = self._get_commands(profile, 'commands')
        if self.ignore_default_keybindings:
            self._remove_key_bindings(data)
        user_data = self._get_commands(profile, 'user_commands')
        self._rupdate(data, user_data)
        defaults = self._merge_platform_specific_tags(profile.get('defaults', _DEFAULT_DEFAULTS))
        for key, item in data.items():
            try:
                args = dict(defaults)
                args.update(item)
                args['flags'] = flags.from_string(str(args['flags']))
                if flags.check_platform(args['flags']):
                    if args['keys']:
                        args['keys'] = self._map_keybinding(args['keys'])
                    self.commands[key] = Command(**args)
            except Exception as exception:
                suricate.log('WARNING: Command %r not added: %s', key, exception)

    @staticmethod
    def _rupdate(lhs, rhs):
        for key, irhs in rhs.items():
            ilhs = lhs.get(key, {})
            ilhs.update(irhs)
            lhs[key] = ilhs

    @staticmethod
    def _remove_key_bindings(data):
        for item in data.values():
            if 'keys' in item:
                item.pop('keys')

    def _get_commands(self, profile, key):
        data = profile.get(key, {})
        return dict((k, self._merge_platform_specific_tags(v)) for k, v in data.items())

    @staticmethod
    def _merge_platform_specific_tags(raw_data):
        data = {}
        for tag in _TAG_LIST:
            os_tag = tag + '.' + _PLATFORM
            if os_tag in raw_data:
                data[tag] = raw_data[os_tag]
            elif tag in raw_data:
                data[tag] = raw_data[tag]
        return data

    def _map_keybinding(self, keybinding):
        # Override <c>+o.
        if self.override_ctrl_o and keybinding[0] == '<c>+o':
            keybinding = [self.override_ctrl_o] + keybinding[1:]
        # Map keys by platform.
        for key, value in self.os_key_map.items():
            keybinding = [x.replace(key, value) for x in keybinding]
        return keybinding


def parse_profiles(profiles):
    assert suricate.api_is_ready()
    parser = _CommandParser(suricate.load_settings())
    for profile_file_name in profiles:
        profile = sublime.load_settings(profile_file_name)
        parser.parse(profile)
    return parser.commands
