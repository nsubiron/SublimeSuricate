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

"""Retrieve the current file project."""

import sublime

if sublime.version() > '3000':

  def get_project_file():
      """Return the current project file."""
      return sublime.active_window().project_file_name()

else:

  # Workaround to retrieve the project file from sublime session files.

  import json
  import os
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

  def get_project_file():
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
