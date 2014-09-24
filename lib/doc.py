# Sublime Suricate, Copyright (C) 2013 N. Subiron
#
# This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you
# are welcome to redistribute it and/or modify it under the terms of the GNU
# General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.

"""Basic tools to parse python files and generate documentation."""

import os
import inspect

from collections import namedtuple
from suricate import import_module
from suricate import pybase

ModuleInfo = namedtuple('ModuleInfo', ['name', 'doc', 'functions'])
RoutineInfo = namedtuple('RoutineInfo', ['signature', 'doc'])

def routine(funcobj):
    """Retrieve signature as string of funcobj."""
    argspec = inspect.getargspec(funcobj)
    sign = []
    dsize = 0 if not argspec.defaults else len(argspec.defaults)
    getd = lambda x: "'%s'" % x if isinstance(x, pybase.string_types) else x
    for i, arg in enumerate(argspec.args, dsize - len(argspec.args)):
      sign.append(arg + ('' if i<0 else '=%s' % getd(argspec.defaults[i])))
    if argspec.varargs:
      sign.append('*%s' % argspec.varargs)
    if argspec.keywords:
      sign.append('**%s' % argspec.keywords)
    return RoutineInfo('%s(%s)' % (funcobj.__name__, ', '.join(sign)), funcobj.__doc__)

def module(module_name, path, metaname=None):
    """Retrieve information of module's routines. Note: the module is
    reloaded."""
    if metaname is None:
      metaname = module_name
    try:
      module = import_module('lib.' + module_name)
      info = ModuleInfo(metaname, module.__doc__, [])
      for obj_name in [x for x in dir(module) if not x.startswith('_')]:
        obj = getattr(module, obj_name)
        if inspect.isfunction(obj) and obj.__module__ == module.__name__:
          info.functions.append(routine(obj))
      return info
    except Exception as e:
      info = '%s: %s' % (type(e).__name__, ', '.join(e.args))
      return ModuleInfo(metaname, info, [])

def folder(path, parents=[]):
    path = os.path.abspath(path)
    for item in [x for x in os.listdir(path) if not x.startswith('_')]:
      itempath = os.path.join(path, item)
      if os.path.isdir(itempath):
        for info in folder(item, parents+[item]):
          yield info
      elif item.endswith('.py'):
        basename = item[:-3]
        yield module(basename, path, '.'.join(parents+[basename]))

def markdown(generator, level=1, indent=0, indentstr='  '):
    getdoc = lambda info: '' if info.doc is None else info.doc+'\n'
    for info in generator():
      if isinstance(info, ModuleInfo):
        yield '%s%s %s' % (indentstr*indent, '#'*level, info.name)
        for line in getdoc(info).split('\n'):
          yield '%s%s' % (indentstr*indent, line.strip())
        for line in markdown(lambda: info.functions, level, indent, indentstr):
          yield line
      elif isinstance(info, RoutineInfo):
        yield '%s* ``%s``' % (indentstr*indent, info.signature)
        for line in getdoc(info).split('\n'):
          yield '%s%s' % (indentstr*(indent+1), line.strip())
      else:
        raise Exception('Invalid info type!')

def to_buffer(title, root):
    from . import sublime_wrapper
    text = '%s\n%s\n\n' % (title, '='*len(title))
    text += '## modules\n\n'
    text += '\n'.join(line for line in markdown(lambda: folder(root), 3))
    sublime_wrapper.flush_to_buffer(text, name=title, scratch=True, syntax='Markdown')
