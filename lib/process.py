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
import subprocess

from threading import Thread

from . import sublime_wrapper


def _filter(obj):
    return sublime_wrapper.expand_build_variables(obj)

def system(command):
    command = _filter(command)
    print('Executing: ' + command)
    return os.system(command)

def system_quiet(command):
    """May not work!"""
    command = _filter(command)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.call(command, startupinfo=startupinfo)

def popen(*args, **kwargs):
    """Wait until the subprocess finishes and return (out, err)."""
    return _popen_internal(*_filter(args), **_filter(kwargs)).communicate()

def new_thread(*args, **kwargs):
    """Call popen and wait until finishes within a new thread so Sublime Text do
    not freezes. Print stdout and show error message if stderr."""
    args, kwargs = _filter((args, kwargs))
    class MyThread(Thread):
        def run(self):
            out, err = _popen_internal(*args, **kwargs).communicate()
            m = 'Subprocess finished.'
            sublime.set_timeout(lambda: sublime.status_message(m), 10)
            print(out)
            if err:
              sublime.error_message(err)
    thread = MyThread()
    thread.start()

__is_windows = sublime.platform().lower() == 'windows'
def _popen_internal(cmd=[], working_dir=None, shell=__is_windows):
    print('popen: %s' % ' '.join(cmd))
    kwargs = {'cwd': working_dir, 'stdout': subprocess.PIPE, 'shell': shell}
    process = subprocess.Popen(cmd, **kwargs)
    return process

def start_file(path):
    """@todo Get rid of this function.
    Try to emulate the behavior of double-clicking the file. Not really
    successful for linux: if the file has execution permissions execute it in a
    terminal, ``xdg-open`` otherwise."""
    path = _filter(path)
    platform = sublime.platform()
    if not os.access(path, os.F_OK):
      return sublime.error_message('File not found!\n%s' % path)
    if platform == 'windows':
      os.startfile(path)
    elif platform == 'linux':
      if os.access(path, os.X_OK):
        system('gnome-terminal --maximize -x bash -c \"' + path + '\"')
      else:
        system('xdg-open \"' + path + '\"')
    else:
      sublime.error_message('Plugin not implemented for this platform!')
