# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Extract and expand Sublime Text build variables.

Build variables:
  * ``${file}`` The full path to the current file, e. g., C:\\Files\\Chapter1.txt.
  * ``${file_base_name}`` The name only portion of the current file, e. g., Document.
  * ``${file_extension}`` The extension portion of the current file, e. g., txt.
  * ``${file_name}`` The name portion of the current file, e. g., Chapter1.txt.
  * ``${file_path}`` The directory of the current file, e. g., C:\\Files.
  * ``${packages}`` The full path to the Packages folder.
  * ``${project}`` The full path to the current project file.
  * ``${project_base_name}`` The name only portion of the current project file.
  * ``${project_extension}`` The extension portion of the current project file.
  * ``${project_name}`` The name portion of the current project file.
  * ``${project_path}`` The directory of the current project file.
"""

import sublime


if sublime.version() > '3068':

    def extract_window_variables(window):
        return window.extract_variables()

    def expand_variables(value, variables):
        return sublime.expand_variables(value, variables)


else:

    import logging
    import os
    import re

    def extract_window_variables(window):
        variables = {}
        try:
            view = window.active_view()
            variables['packages'] = sublime.packages_path()

            def _add_file(key, path):
                if path:
                    folder, file_name = os.path.split(path)
                    base_name, extension = os.path.splitext(file_name)
                    variables[key] = path
                    variables['%s_path' % key] = folder
                    variables['%s_name' % key] = file_name
                    variables['%s_extension' % key] = extension
                    variables['%s_base_name' % key] = base_name
            if view is None:
                view = sublime.active_window().active_view()
            if view is not None:
                _add_file('file', view.file_name())
            _add_file('project', window.project_file_name())
        except:
            logging.exception('Error retrieving build variables')
        return variables

    def expand_variables(value, variables):
        if isinstance(value, str):
            for key, item in variables.items():
                value = re.sub(r'(\$\{%s\})' % key, value, item)
            return value
        elif isinstance(value, (list, tuple, range, set, frozenset)):
            return type(value)(expand_variables(x) for x in value)
        elif isinstance(value, dict):
            return dict((k, expand_variables(v)) for k, v in value.items())
        else:
            return value
