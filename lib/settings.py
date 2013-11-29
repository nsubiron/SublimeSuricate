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

from suricate import SettingsFileBaseName

def toggle_boolean(key, base_name=SettingsFileBaseName):
    settings = sublime.load_settings(base_name)
    value = settings.get(key)
    if isinstance(value, bool):
      settings.set(key, not value)
      sublime.save_settings(base_name)
    else:
      sublime.error_message('Cannot toggle a non-boolean object "%s"' % key)
