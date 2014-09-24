# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import os
import sublime

SettingsFileBaseName = 'Suricate.sublime-settings'

__this_folder__ = os.path.dirname(os.path.abspath(__file__))

if __this_folder__.endswith('.sublime-package'):
  SuricatePackagePath = __this_folder__
else:
  SuricatePackagePath = os.path.abspath(os.path.join(__this_folder__, '..'))

SuricateBaseName, _ = os.path.splitext(os.path.basename(SuricatePackagePath))

SuricatePath = os.path.abspath(os.path.join(sublime.packages_path(), SuricateBaseName))

LibName = 'lib'

LibFolder = os.path.join(SuricatePackagePath, LibName)

SuricateVariables = {
  'suricate_base_name': SuricateBaseName,
  'suricate_package_path': SuricatePackagePath,
  'suricate_path': SuricatePath
}

_clean = lambda p: '/' + p.replace(os.sep, '/').replace(':', '')

SuricateMenuVariables = {
  'suricate_base_name': SuricateBaseName,
  'suricate_package_path': '${packages}/' + SuricateBaseName,
  'suricate_path': '${packages}/' + SuricateBaseName
}
