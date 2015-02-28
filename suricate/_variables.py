# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Sublime Text build variables:
  * ``${file}`` The full path to the current file, e. g., C:\Files\Chapter1.txt.
  * ``${file_base_name}`` The name only portion of the current file, e. g., Document.
  * ``${file_extension}`` The extension portion of the current file, e. g., txt.
  * ``${file_name}`` The name portion of the current file, e. g., Chapter1.txt.
  * ``${file_path}`` The directory of the current file, e. g., C:\Files.
  * ``${packages}`` The full path to the Packages folder.
  * ``${project}`` The full path to the current project file.
  * ``${project_base_name}`` The name only portion of the current project file.
  * ``${project_extension}`` The extension portion of the current project file.
  * ``${project_name}`` The name portion of the current project file.
  * ``${project_path}`` The directory of the current project file.
Suricate variables:
  * ``suricate_base_name`` The base name of the suricate package.
  * ``suricate_path`` The full path to the suricate folder under Packages folder.
  * ``suricate_package_path`` The full installation path of the suricate package."""

import logging
import os

import sublime

from . import defs
from . import util

def get(view=None):
    """Get a dictionary with the available build variables."""
    vmap = defs.SuricateVariables
    try:
      vmap['packages'] = sublime.packages_path()
      def _add_file(key, path):
          if path:
            folder, file_name = os.path.split(path)
            base_name, extension = os.path.splitext(file_name)
            vmap[key] = path
            vmap['%s_path' % key] = folder
            vmap['%s_name' % key] = file_name
            vmap['%s_extension' % key] = extension
            vmap['%s_base_name' % key] = base_name
      if view is None:
        view = sublime.active_window().active_view()
      if view is not None:
        _add_file('file', view.file_name())
      window = sublime.active_window() if view is None else view.window()
      _add_file('project', window.project_file_name())
    except:
      logging.exception('Error retrieving build variables')
    finally:
      return vmap

def expand(obj, view=None):
    """Expand available build variables in object."""
    return util.replacekeys(obj, get(view))
