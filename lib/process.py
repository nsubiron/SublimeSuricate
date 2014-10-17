# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import os
import sublime
import subprocess

from threading import Thread

from suricate import Verbose
from suricate import build_variables
from suricate import pybase

if pybase.PY2:
  def decode(string):
      return None if string is None else unicode(string, 'utf-8')
else:
  def decode(bstring):
      return None if bstring is None else bstring.decode('utf-8')

def touch(paths, times=None):
    for path in paths:
      with open(path, 'a'):
        os.utime(path, times)

def _filter(obj):
    # @todo Needed?
    return build_variables.expand(obj)

def system(command):
    command = _filter(command)
    if Verbose: print('Executing: ' + command)
    return os.system(command)

def system_quiet(command):
    """May not work!"""
    command = _filter(command)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return subprocess.call(command, startupinfo=startupinfo)

def popen(*args, **kwargs):
    """Wait until the subprocess finishes and return (out, err)."""
    return _popen_internal(*_filter(args), **_filter(kwargs))

def new_thread(*args, **kwargs):
    """Call popen and wait until finishes within a new thread so Sublime Text
    does not freeze. Print stdout and show error message if stderr."""
    args, kwargs = _filter((args, kwargs))
    class MyThread(Thread):
        def run(self):
            out, err = _popen_internal(*args, **kwargs)
            m = 'Subprocess finished.'
            sublime.set_timeout(lambda: sublime.status_message(m), 10)
            print(out)
            if err:
              sublime.error_message(err)
    thread = MyThread()
    thread.start()

__is_windows = sublime.platform().lower() == 'windows'
def _popen_internal(cmd=[], working_dir=None, shell=__is_windows):
    if Verbose: print('popen: %s' % ' '.join(cmd))
    kwargs = {'cwd': working_dir, 'stdout': subprocess.PIPE, 'shell': shell}
    process = subprocess.Popen(cmd, **kwargs)
    if pybase.PY2:
      out, err = process.communicate()
    else:
      try:
        out, err = process.communicate(timeout=15)
      except subprocess.TimeoutExpired:
        print('WARNING: suricate: timeout expired, killing the process...')
        process.kill()
        out, err = process.communicate()
    if err:
      print('WARNING: suricate: subprocess returned error: %s' % decode(err))
    return decode(out), decode(err)

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
