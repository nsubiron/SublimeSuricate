# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import sublime

from suricate import defs

def toggle_boolean(key, base_name=defs.SettingsFileBaseName):
    settings = sublime.load_settings(base_name)
    value = settings.get(key)
    if isinstance(value, bool):
      settings.set(key, not value)
      sublime.save_settings(base_name)
    else:
      sublime.error_message('Cannot toggle a non-boolean object "%s"' % key)
