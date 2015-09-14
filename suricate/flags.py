# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Bitwise flags definitions and operations."""

import fnmatch
import os
import re

import sublime

from . import _suricate as suricate

from functools import reduce

class Flags(object):
    EMPTY                 = 0x0000
    # Platforms.
    Linux                 = 0x0001
    Windows               = 0x0002
    OSX                   = 0x0004
    # Version control systems.
    Git                   = 0x0010
    Svn                   = 0x0020
    Surround              = 0x0040
    # File types.
    IsFile                = 0x0100
    IsDir                 = 0x0200
    # Other.
    SuricateIsPackaged    = 0x1000
    SuricateIsNotPackaged = 0x2000
    # Never active.
    Never                 = 0x8000

ExorGroups = [
  (Flags.Linux|Flags.Windows|Flags.OSX, True),
  (Flags.Svn|Flags.Surround|Flags.Git, False)
]

VCS_FDS = [('.git', Flags.Git), ('.svn', Flags.Svn), ('.MySCMServerInfo', Flags.Surround)]

def check(flags, needed):
    """Check whether flags satisfy needed."""
    return flags&needed == needed

def checkany(flags, needed, empty=False):
    return flags&needed>=Flags.EMPTY if empty else flags&needed>Flags.EMPTY

def special_check(flags, needed):
    def f(f, n, e):
        if n&e>0:
          return checkany(f, n&e)
        else:
          return True
    a = reduce(lambda x, y: x|y, [a for a,b in ExorGroups], flags)
    return all(f(flags, needed, exor) for exor, empty in ExorGroups) and check(a, needed)

def from_string(string):
    """Convert a String formatted as 'Flag1|Flag2|...' to bitwise flag."""
    add = lambda f, n: f|getattr(Flags, n, Flags.EMPTY)
    return reduce(add, string.split('|'), Flags.EMPTY)

STRMAP = dict((getattr(Flags,n),n) for n in dir(Flags) if not n.startswith('_'))
del STRMAP[Flags.EMPTY]
def to_string(flags):
    return '|'.join(n for f, n in STRMAP.items() if check(flags, f))

PLATFORM = from_string(sublime.platform().title())

IS_PACKAGED = (Flags.SuricateIsPackaged if suricate.is_packaged() else Flags.SuricateIsNotPackaged)

def check_platform(flags):
    """Return whether flags match current platform."""
    return check(flags, PLATFORM) or \
           (Flags.Linux|Flags.Windows|Flags.OSX)&flags==Flags.EMPTY

def parse(path):
    """Retrieve active flags from path."""
    if path is None:
      return PLATFORM|IS_PACKAGED
    if os.path.isfile(path):
      folder, name = os.path.split(path)
      return PLATFORM|IS_PACKAGED|Flags.IsFile|_vcs(folder)
    elif os.path.isdir(path):
      return PLATFORM|IS_PACKAGED|Flags.IsDir|_vcs(path)

def get_vcs(path):
    if os.path.isfile(path):
      path, _ = os.path.split(path)
    return _vcs(path)

## Internal ####################################################################

def _parseft(pattern, flag):
    r = re.compile(fnmatch.translate(pattern))
    return lambda filename: flag if r.match(filename) else Flags.EMPTY

class _VcsChecker(object):
    def __init__(self):
        # @todo ignore paths.
        self.map = {}

    def __call__(self, path):
        for key, flag in self.map.items():
          if key in path:
            return flag
        for sub in _iterate_path(path):
          for item, flag in VCS_FDS:
            item_path = os.path.join(sub, item)
            if os.path.isdir(item_path) or os.path.isfile(item_path):
              self.map[sub] = flag
              return flag
        return Flags.EMPTY

_vcs = _VcsChecker()

def _iterate_path(path):
    drive, path = os.path.splitdrive(path)
    sub = drive + os.sep
    for item in [x for x in path.split(os.sep) if x]:
      # @todo use iterators.
      yield sub
      sub = os.path.join(sub, item)
    yield sub
