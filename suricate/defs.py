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

import os
import sublime

SettingsFileBaseName = 'Suricate.sublime-settings'

__this_folder__ = os.path.dirname(os.path.abspath(__file__))

SuricatePackagePath = os.path.abspath(os.path.join(__this_folder__, '..'))

SuricateBaseName = os.path.basename(SuricatePackagePath)

SuricatePath = os.path.abspath(os.path.join(sublime.packages_path(), SuricateBaseName))

LibName = 'lib'

LibFolder = os.path.join(SuricatePackagePath, LibName)

SuricateVariables = {
  'suricate_base_name': SuricateBaseName,
  'suricate_package_path': SuricatePackagePath,
  'suricate_path': SuricatePath
}

_clean = lambda p: '/' + p.replace(os.sep, '/').replace(':', '')
SuricateMenuVariables = dict((k, _clean(v)) for k, v in SuricateVariables.items())
