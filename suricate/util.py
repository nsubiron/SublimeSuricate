# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import fnmatch
import os
import stat
import re
import shutil
import sublime

from . import pybase

from datetime import datetime
from contextlib import contextmanager

@contextmanager
def pushd(directory):
    """Context manager to temporally change working directory. Yields None."""
    cwd = os.getcwd()
    try:
      os.chdir(directory)
      yield
    finally:
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

def regex_callable(patterns):
    """Return a callable object that returns True if matches any regular
    expression in patterns"""
    if patterns is None:
      return lambda x: False
    if isinstance(patterns, str):
      patterns = [patterns]
    r = re.compile(r'|'.join(fnmatch.translate(p) for p in patterns))
    return lambda x: r.match(x) is not None

def walk(root, file_includes=['*'], file_excludes=None, dir_excludes=['.git', '.svn'], followlinks=False):
    """Convenient wrap around os.walk. Patterns are checked on base names, not
    on full path names."""
    fincl = regex_callable(file_includes)
    fexcl = regex_callable(file_excludes)
    dexcl = regex_callable(dir_excludes)
    for path, dirs, files in os.walk(os.path.abspath(root), followlinks=followlinks):
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

def make_list(obj):
    if obj is None:
      return []
    elif isinstance(obj, pybase.sequence_types + pybase.set_types):
      return list(obj)
    elif isinstance(obj, pybase.mapping_types):
      return [[key, value] for key, value in obj.items()]
    else:
      return [obj]

def replacekeys(obj, dictionary):
    """Replace any ${key} occurrence in obj by its value in dictionary."""
    if obj is None:
      return None
    elif isinstance(obj, pybase.string_types):
      for key, value in dictionary.items():
        obj = obj.replace('${%s}' % key, value)
      return obj
    elif isinstance(obj, dict):
      return dict((k, replacekeys(i, dictionary)) for k, i in obj.items())
    elif isinstance(obj, pybase.sequence_types) or isinstance(obj, pybase.set_types):
      return type(obj)(replacekeys(i, dictionary) for i in obj)
    elif isinstance(obj, bool) or isinstance(obj, pybase.numeric_types):
      return obj
    else:
      raise Exception('Type object \'%s\' not implemented.' % type(obj))
