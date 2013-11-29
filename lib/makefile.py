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

from suricate import reload_module

sublime_wrapper =reload_module('lib.sublime_wrapper')

def make(makefile, target=None):
    folder = os.path.dirname(makefile)
    on_done = lambda target: sublime_wrapper.execute(cmd=['make', target], working_dir=folder)
    if target is None:
      with open(makefile, 'r') as f:
        _starts = lambda l: not any(l.startswith(p) for p in ['.', '$', '_', '\t'])
        _contains = lambda l: ':' in l and '=' not in l
        is_target = lambda l: _starts(l) and _contains(l)
        targets = [l[0:l.find(':')] for l in f if is_target(l)]
      sublime_wrapper.show_quick_panel(targets, on_done)
    else:
      on_done(target)
