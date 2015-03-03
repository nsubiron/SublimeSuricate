# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import sublime

import suricate
from suricate import command_parser

from . import sublime_wrapper

suricate.reload_module(sublime_wrapper)


def find_profiles():
    extension = suricate.get_variable('suricate_profile_extension')
    lst = sublime.find_resources('*' + extension)
    return set(x.rsplit('/', 1)[-1][:-len(extension)] for x in lst)


def _get_current_profile_set():
    return set(suricate.get_setting('profiles', []))


def _set_and_save_profiles(value):
    variable_name = 'suricate_settings_file_base_name'
    settings_file_base_name = suricate.get_variable(variable_name)
    settings = sublime.load_settings(settings_file_base_name)
    settings.set('profiles', list(value))
    sublime.save_settings(settings_file_base_name)


def add():
    display_list = []
    extension = suricate.get_variable('suricate_profile_extension')
    current = _get_current_profile_set()
    for profile in find_profiles().difference(current):
        settings = sublime.load_settings(profile + extension)
        description = settings.get('description', 'No description provided')
        display_list.append([profile, description])
    if not display_list:
        sublime.error_message(
            'Sorry, you already have all the profiles active.')
        return

    def on_done(picked):
        current.add(picked[0])
        _set_and_save_profiles(current)
    sublime_wrapper.show_quick_panel(sorted(display_list), on_done)


def remove():
    display_list = []
    extension = suricate.get_variable('suricate_profile_extension')
    current = _get_current_profile_set()
    for profile in current:
        settings = sublime.load_settings(profile + extension)
        description = settings.get('description', 'No description provided')
        display_list.append([profile, description])
    if not display_list:
        sublime.error_message('Sorry, you don\'t have any active profile.')
        return

    def on_done(picked):
        current.remove(picked[0])
        _set_and_save_profiles(current)
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
    return '\n'.join(indentation * ' ' + c.ljust(maxcaption + 4) + ','.join(k) for g, c, k in lst)


def to_buffer():
    title = 'Profiles'
    text = '%s\n%s\n\n' % (title, '=' * len(title))
    extension = suricate.get_variable('suricate_profile_extension')
    current = _get_current_profile_set()
    no_keybindings = suricate.get_setting('ignore_default_keybindings', False)
    profiles = [['Your profile', current]] + [[x, [x]] for x in find_profiles()]
    for name, profile_names in profiles:
        profile_files = [x + extension for x in profile_names]
        text += '### %s\n\n' % name
        commands = command_parser.parse_profiles(profile_files, no_keybindings)
        text += print_commands(commands) + '\n\n'
    sublime_wrapper.flush_to_buffer(
        text,
        name=title,
        scratch=True,
        syntax='Markdown')
