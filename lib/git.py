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
import sublime_wrapper
import util

def touch(fname, times=None):
    with file(fname, 'a'):
      os.utime(fname, times)

def clean_repo(working_dir):
    working_dir = os.path.abspath(working_dir)
    gitignore = os.path.join(working_dir, '.gitignore')
    f = open(gitignore, 'r')
    try:
      patterns = [x[:-1] for x in f.readlines()]
    finally:
      f.close()
    util.recursively_remove(working_dir, patterns)

def _on_clone_user_settings(repository):
    """Backup User folder and clone 'repository' on it."""
    PackagesFolder = sublime.packages_path()
    UserFolder = os.path.join(PackagesFolder, 'User')
    BackupFolder = os.path.abspath(os.path.join(PackagesFolder, '../Backup'))
    dst = util.backup(UserFolder, BackupFolder)
    sublime.message_dialog("Backup saved at '%s'" % dst)
    util.forcermtree(UserFolder)
    cmd = ['git', 'clone', repository, UserFolder]
    sublime_wrapper.execute(cmd=cmd, working_dir=PackagesFolder)
    # @todo If fails restore from the backup.

def clone_user_settings():
    window=sublime.active_window()
    caption = 'git clone %s ${packages}/User'
    window.show_input_panel(caption, '', _on_clone_user_settings, None, None)
