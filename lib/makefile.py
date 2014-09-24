# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

import os

from suricate import import_module

sublime_wrapper = import_module('lib.sublime_wrapper')

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
