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

import suricate

from suricate import commands as command_parser
from suricate import defs

from . import sublime_wrapper

Extension = command_parser.ProfileExtension
SettingsKey = 'profiles'

if sublime.version() < '3000':

  import os

  from suricate import util

  def find_profiles():
      lst = list(util.fwalk(sublime.packages_path(), ['*' + Extension]))
      return set(os.path.splitext(os.path.basename(x))[0] for x in lst)

else:

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
      sublime.error_message('Sorry, you already have all the profiles active.')
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
        maxcaption = max(maxcaption, len(command.func))
        lst.append([str(command.group), command.func, command.keys])
    lst.sort()
    return '\n'.join(indentation*' ' + c.ljust(maxcaption+4) + ','.join(k) for g,c,k in lst)

def to_buffer():
    title = 'Profiles'
    text = '%s\n%s\n\n' % (title, '='*len(title))
    current = suricate.Settings.get(SettingsKey, [])
    profiles = [['Your profile', current]] + [[x,[x]] for x in find_profiles()]
    print(profiles)
    for name, profile in profiles:
      text += '### %s\n\n' % name
      text += print_commands(command_parser.get(profile)) + '\n\n'
    sublime_wrapper.flush_to_buffer(text, name=title, scratch=True, syntax='Markdown')
