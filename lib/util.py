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

import fnmatch
import os
import stat
import re
import shutil
import sublime

from datetime import datetime
from contextlib import contextmanager

# Python 2 and 3 compatibility.
import sys
PY2 = sys.version_info[0] == 2
if not PY2:
  text_type = str
  string_types = (str,)
  ignore_replace_types = (bool, int, float, complex)
  unichr = chr
else:
  text_type = unicode
  string_types = (str, unicode)
  ignore_replace_types = (bool, int, float, long, complex)
  unichr = unichr

@contextmanager
def pushd(directory):
    """Context manager to temporally change working directory."""
    cwd = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(cwd)

DefaultPathExt = ['']
if sublime.platform().lower() == 'windows':
  DefaultPathExt += ['.com', '.exe', '.bat', '.cmd']

def which(name, flags=os.X_OK, pathext=DefaultPathExt):
    """Return the full path to the first executable found in the environmental
    variable PATH matching the given name."""
    envpath = os.environ.get('PATH', None)
    if envpath is None:
      return None
    exts = set(os.environ.get('PATHEXT', '').split(os.pathsep) + pathext)
    for path in envpath.split(os.pathsep):
      pname = os.path.join(path, name)
      if os.access(pname, flags):
        return pname
      for ext in exts:
        pnameext = pname + ext
        if os.access(pnameext, flags):
          return pnameext
    return None

def toggle_read_only(path='${file}'):
    import sublime_wrapper
    path = sublime_wrapper.expand_build_variables(path)
    if os.access(path, os.W_OK):
      os.chmod(path, stat.S_IREAD)
    else:
      os.chmod(path, stat.S_IWRITE)

def regex_callable(patterns):
    """Return a callable object that returns True if matches any regular
    expression in patterns"""
    if patterns is None:
      return lambda x: False
    if isinstance(patterns, str):
      patterns = [patterns]
    r = re.compile(r'|'.join(fnmatch.translate(p) for p in patterns))
    return lambda x: r.match(x) is not None

def walk(root, file_includes=['*'], file_excludes=None, dir_excludes=['.git', '.svn']):
    """Convenient wrap around os.walk. Patterns are checked on base names, not
    on full path names."""
    fincl = regex_callable(file_includes)
    fexcl = regex_callable(file_excludes)
    dexcl = regex_callable(dir_excludes)
    for path, dirs, files in os.walk(os.path.abspath(root)):
      dirs[:] = [d for d in dirs if not dexcl(d)]
      files[:] = [f for f in files if fincl(f) and not fexcl(f)]
      yield path, dirs, files

def fwalk(*args, **kwargs):
    """Walk over the full path of the files matching the arguments given. See
    util.walk."""
    for path, _, files in walk(*args, **kwargs):
      for f in files:
        yield os.path.join(path, f)

def recursively_remove(*args, **kwargs):
    """Recursively remove files matching a pattern. See util.walk"""
    for path in fwalk(*args, **kwargs):
      os.remove(path)

def forcermtree(directory):
    """Force deletion (including read-only files) of an entire directory tree;
    path must point to a directory (but not a symbolic link to a directory). See
    shutil.rmtree."""
    def _onerror(func, path, exc_info):
        """Error handler for read only files on 'shutil.rmtree'."""
        if os.access(path, os.W_OK):
          raise
        os.chmod(path, stat.S_IWUSR)
        func(path)
    shutil.rmtree(directory, onerror=_onerror)

def backup(src, dst, symlinks=False, ignore=None, timepattern='%Y%m%d%H%M%S'):
    """Creates a datetime-name-based subfolder under dst containing src, see
    shutil.copytree. Returns the final destination folder."""
    src = os.path.abspath(src)
    date_t = datetime.now().strftime(timepattern)
    dst = os.path.join(os.path.abspath(dst), date_t, os.path.basename(src))
    shutil.copytree(src, dst, symlinks, ignore)
    return dst

def replacekeys(obj, dictionary):
    """Replace any ${key} occurrence in obj by its value in dictionary."""
    if obj is None:
      return None
    elif isinstance(obj, string_types):
      for key, value in dictionary.items():
        obj = obj.replace('${%s}' % key, value)
      return obj
    elif isinstance(obj, dict):
      return dict((k, replacekeys(i, dictionary)) for k, i in obj.items())
    elif isinstance(obj, (tuple, list, set)):
      return type(obj)(replacekeys(i, dictionary) for i in obj)
    elif isinstance(obj, ignore_replace_types):
      return obj
    else:
      raise Exception('Type object \'%s\' not implemented.' % type(obj))
