# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import sublime

import suricate

from suricate import commands as command_parser
from suricate import defs

from . import sublime_wrapper

Extension = command_parser.ProfileExtension
SettingsKey = 'profiles'


def find_profiles():
    lst = sublime.find_resources('*' + Extension)
    return set(x.rsplit('/', 1)[-1][:-len(Extension)] for x in lst)


def add():
    display_list = []
    current = suricate.Settings.get(SettingsKey, [])
    for profile in find_profiles().difference(set(current)):
        settings = sublime.load_settings(profile + Extension)
        description = settings.get('description', 'No description provided')
        display_list.append([profile, description])
    if not display_list:
        sublime.error_message(
            'Sorry, you already have all the profiles active.')
        return

    def on_done(picked):
        suricate.Settings.set(SettingsKey, current + [picked[0]])
        sublime.save_settings(defs.SettingsFileBaseName)
    sublime_wrapper.show_quick_panel(sorted(display_list), on_done)


def remove():
    display_list = []
    current = suricate.Settings.get(SettingsKey, [])
    for profile in current:
        settings = sublime.load_settings(profile + Extension)
        description = settings.get('description', 'No description provided')
        display_list.append([profile, description])
    if not display_list:
        sublime.error_message('Sorry, you don\'t have any active profile.')
        return

    def on_done(picked):
        current.remove(picked[0])
        suricate.Settings.set(SettingsKey, current)
        sublime.save_settings(defs.SettingsFileBaseName)
    sublime_wrapper.show_quick_panel(sorted(display_list), on_done)


def print_commands(commands, indentation=4, minsep=10):
    lst = []
    maxcaption = minsep
    for command in commands.values():
        if command.caption:
            maxcaption = max(maxcaption, len(command.caption))
            lst.append([str(command.group), command.caption, command.keys])
        else:
            maxcaption = max(maxcaption, len(command.call))
            lst.append([str(command.group), command.call, command.keys])
    lst.sort()
    return '\n'.join(
        indentation *
        ' ' +
        c.ljust(
            maxcaption +
            4) +
        ','.join(k) for g,
        c,
        k in lst)


def to_buffer():
    title = 'Profiles'
    text = '%s\n%s\n\n' % (title, '=' * len(title))
    current = suricate.Settings.get(SettingsKey, [])
    no_keybindings = suricate.Settings.get('ignore_default_keybindings', False)
    profiles = [['Your profile', current]] + [[x, [x]]
                                              for x in find_profiles()]
    for name, profile in profiles:
        text += '### %s\n\n' % name
        text += print_commands(command_parser.get(profile,
                                                  no_keybindings)) + '\n\n'
    sublime_wrapper.flush_to_buffer(
        text,
        name=title,
        scratch=True,
        syntax='Markdown')
