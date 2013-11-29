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
  * ``${project_path}`` The directory of the current project file."""

import os
import sublime

from . import util

def get(view=None):
    """Get a dictionary with the available build variables."""
    vmap = {}
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
      _add_file('project', project_file())
    finally:
      return vmap

def expand(obj, view=None):
    """Expand available build variables in object."""
    return util.replacekeys(obj, get(view))

if sublime.version() > '3000':

  def project_file():
      """Return the current project file."""
      return sublime.active_window().project_file_name()

else:

  # Workaround for Sublime Text 2 to retrieve the project file from sublime
  # session files.

  import json
  import re

  _abs = lambda p: os.path.abspath(p)
  _absre = lambda p: os.path.abspath(re.sub(r'^/([^/])/', '\\1:/', p))

  def _load_json_file(path):
      with open(os.path.normpath(path), 'r') as f:
        data = f.read()
        return json.loads(data.replace('\t', ' '), strict=False)

  class _ProjectParser(object):
      """Check whether a project matches open folders in active window."""

      def __init__(self):
          self.current = None
          self.folders = []

      def iscurrent(self):
          return self._check_folders(self.folders, init=True)

      def _check_folders(self, folders, init=True):
          if init:
            self.wfolders = sorted(_abs(p) for p in sublime.active_window().folders())
            self.number_of_folders = len(self.wfolders)
          return len(folders) == self.number_of_folders and \
                 all(folders[x]==self.wfolders[x] for x in xrange(0, self.number_of_folders))

      def parse(self, projects):
          for project in [p for p in projects if p]:
            project = _absre(project)
            print('Parsing project file "%s"' % project)
            project_json = _load_json_file(project)
            project_folders = sorted(_absre(f['path']) for f in project_json.get('folders', []))
            if self._check_folders(project_folders, init=False):
              self.current = project
              self.folders = project_folders
              return True
          return False

  _parser = _ProjectParser()

  def project_file():
      """Return the current project file."""
      if _parser.iscurrent():
        return _parser.current
      sfolder = _abs(os.path.join(sublime.packages_path(), '..', 'Settings'))
      data = _load_json_file(os.path.join(sfolder, 'Session.sublime_session'))
      projects = set(data['workspaces']['recent_workspaces'])

      if os.path.lexists(os.path.join(sfolder, 'Auto Save Session.sublime_session')):
        data = _load_json_file(os.path.join(sfolder, 'Auto Save Session.sublime_session'))
        if 'workspaces' in data and \
           'recent_workspaces' in data['workspaces'] and \
           data['workspaces']['recent_workspaces']:
          projects += set(data['workspaces']['recent_workspaces'])
      if _parser.parse(projects):
        return _parser.current
      return None
